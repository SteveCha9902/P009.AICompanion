import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { getConversations, createConversation, getMessages } from '../../../services/api';
import { interactionController, InteractionState } from '../../../services/interactionController';
import { voiceController } from '../../../services/voiceController';

interface ConversationViewProps {
  userId: string;
  companionId: string;
  onConversationLoaded?: (conversationId: string) => void;
  onSendText?: (text: string) => void;
  visible?: boolean;
  onClearMessagesRef?: (clearFn: () => void) => void;
  onFocusInputRef?: (focusFn: () => void) => void;
}

export function ConversationView({
  userId,
  companionId,
  onConversationLoaded,
  visible = true,
  onClearMessagesRef,
  onFocusInputRef,
}: ConversationViewProps) {

  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<{ id: string; role: string; content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [interactionState, setInteractionState] = useState<InteractionState>(interactionController.getState());

  const flatListRef = useRef<FlatList>(null);
  const textInputRef = useRef<TextInput>(null);
  const activeInteractionId = useRef<string | null>(null);

  // Expose focus function to parent
  useEffect(() => {
    if (onFocusInputRef) {
      onFocusInputRef(() => {
        textInputRef.current?.focus();
      });
    }
  }, [onFocusInputRef]);

  // Subscribe to VoiceController for real-time voice messages
  useEffect(() => {
    const unsubVoiceMsgs = voiceController.subscribeMessages((userText, assistantText) => {
      setMessages((prev) => {
        const next = [...prev];
        const uText = userText?.trim();
        const aText = assistantText?.trim();

        if (uText) {
          const lastUser = next.filter((m) => m.role === "user").pop();
          if (!lastUser || lastUser.content !== uText) {
            next.push({ id: `voice-user-${Date.now()}`, role: "user", content: uText });
          }
        }
        if (aText) {
          const lastAsst = next.filter((m) => m.role === "assistant").pop();
          if (!lastAsst || lastAsst.content !== aText) {
            next.push({ id: `voice-asst-${Date.now() + 1}`, role: "assistant", content: aText });
          }
        }
        return next;
      });
    });

    return () => {
      unsubVoiceMsgs();
    };
  }, []);

  // Subscribe to central InteractionController
  useEffect(() => {
    const unsubscribe = interactionController.subscribe((state) => {
      setInteractionState(state);

      // Handle streaming assistant message in the list
      if (state.isInteracting && state.status === "streaming" && state.streamingText) {
        const msgId = `asst-${state.currentInteractionId || 'current'}`;
        activeInteractionId.current = state.currentInteractionId;

        setMessages((prev) => {
          const exists = prev.some((m) => m.id === msgId);
          if (!exists) {
            return [...prev, { id: msgId, role: "assistant", content: state.streamingText }];
          } else {
            return prev.map((m) =>
              m.id === msgId ? { ...m, content: state.streamingText } : m
            );
          }
        });
      }

      // When interaction completes, finalize assistant message cleanly without creating duplicates
      if (!state.isInteracting && state.lastCompletedText && activeInteractionId.current) {
        const msgId = `asst-${activeInteractionId.current}`;
        const finalContent = state.lastCompletedText;

        setMessages((prev) => {
          const exists = prev.some((m) => m.id === msgId);
          if (exists) {
            return prev.map((m) => (m.id === msgId ? { ...m, content: finalContent } : m));
          } else {
            return [...prev, { id: msgId, role: "assistant", content: finalContent }];
          }
        });

        // Speak the completed text via VoiceController
        if (finalContent) {
          voiceController.speakText(finalContent);
        }

        activeInteractionId.current = null;
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // Expose clear messages function to parent (creates clean new session)
  useEffect(() => {
    if (onClearMessagesRef) {
      onClearMessagesRef(async () => {
        setMessages([]);
        try {
          const newConv = await createConversation(userId);
          if (newConv && newConv.id) {
            setConversationId(newConv.id);
            if (onConversationLoaded) {
              onConversationLoaded(newConv.id);
            }
          }
        } catch (e) {
          console.warn("[ConversationView] Create new conversation fallback:", e);
        }
      });
    }
  }, [onClearMessagesRef, userId, onConversationLoaded]);

  // Load Conversation History on user or character switch
  useEffect(() => {
    setMessages([]);
    loadConversationHistory();
  }, [userId, companionId]);


  const loadConversationHistory = async () => {
    try {
      setIsLoadingHistory(true);
      // Character-scoped conversation ID
      const charScopedConvId = `conv_${companionId || 'default'}`;
      setConversationId(charScopedConvId);

      // Timeout guard: if backend takes longer than 3.5s, fallback immediately
      const fetchWithTimeout = Promise.race([
        getConversations(userId),
        new Promise<any>((_, reject) => setTimeout(() => reject(new Error("Timeout")), 3500))
      ]);

      const convs = await fetchWithTimeout;
      let targetConvId = charScopedConvId;
      if (convs && convs.length > 0) {
        const found = convs.find((c: any) => c.companion_id === companionId);
        if (found) {
          targetConvId = found.id;
          setConversationId(targetConvId);
        }
        try {
          const msgs = await getMessages(userId, targetConvId);
          setMessages(msgs || []);
        } catch {
          setMessages([]);
        }
      } else {
        setConversationId(charScopedConvId);
        setMessages([]);
      }

      if (onConversationLoaded) {
        onConversationLoaded(targetConvId);
      }
    } catch (err) {
      console.warn("[ConversationView] History load skipped, starting fresh:", err);
      setConversationId("default");
      setMessages([]);
      if (onConversationLoaded) {
        onConversationLoaded("default");
      }
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !conversationId || interactionState.isInteracting) return;

    const userText = input.trim();
    const tempUserMsgId = `user-${Date.now()}`;

    // Optimistically append user message
    setMessages((prev) => [...prev, { id: tempUserMsgId, role: "user", content: userText }]);
    setInput("");
    activeInteractionId.current = null;

    // Send through centralized InteractionController
    await interactionController.sendText(userId, companionId, conversationId, userText);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {visible && (
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View
              style={[
                styles.messageBubble,
                item.role === 'user' ? styles.userBubble : styles.assistantBubble,
              ]}
            >
              <Text style={styles.messageText}>{item.content}</Text>
            </View>
          )}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
          ListEmptyComponent={
            isLoadingHistory ? (
              <View style={styles.inlineLoading}>
                <ActivityIndicator size="small" color="#0A84FF" />
                <Text style={styles.inlineLoadingText}>대화 불러오는 중...</Text>
              </View>
            ) : null
          }
        />
      )}

      {/* When hidden, show subtle spacer */}
      {!visible && <View style={{ flex: 1 }} />}


      {/* Connecting & Thinking Floating Pill */}

      {interactionState.status === "connecting" && (
        <View style={styles.thinkingIndicator}>
          <ActivityIndicator size="small" color="#fff" />
          <Text style={styles.thinkingText}>Genie가 생각 중입니다...</Text>
        </View>
      )}

      {/* Error Toast */}
      {interactionState.error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{interactionState.error}</Text>
        </View>
      )}

      {/* Floating Transparent Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          ref={textInputRef}
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="메시지 입력 (키보드 🎙️로 음성입력 가능)..."
          placeholderTextColor="rgba(255,255,255,0.6)"
          editable={!interactionState.isInteracting}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!input.trim() || interactionState.isInteracting) && styles.sendButtonDisabled,
          ]}
          onPress={handleSend}
          disabled={!input.trim() || interactionState.isInteracting}
        >
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  inlineLoading: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, gap: 8 },
  inlineLoadingText: { color: '#8E8E93', fontSize: 13 },
  listContent: { paddingHorizontal: 16, paddingTop: 6, paddingBottom: 4, flexGrow: 1, justifyContent: 'flex-end' },


  // Ultra-Transparent Floating Glass Bubbles
  messageBubble: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 16,
    marginBottom: 6,
    maxWidth: '75%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.25,
    shadowRadius: 3,
    elevation: 2,
  },
  userBubble: {
    backgroundColor: 'rgba(10, 132, 255, 0.42)',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 3,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.22)',
  },
  assistantBubble: {
    backgroundColor: 'rgba(18, 18, 20, 0.35)',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 3,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  messageText: {
    color: '#ffffff',
    fontSize: 13.5,
    lineHeight: 18.5,
    fontWeight: '400',
    textShadowColor: 'rgba(0, 0, 0, 0.85)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },


  thinkingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(20, 20, 22, 0.75)',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    marginHorizontal: 16,
    marginBottom: 6,
    gap: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)'
  },
  thinkingText: { color: '#e5e5ea', fontSize: 13, fontWeight: '500' },
  errorContainer: { padding: 10, backgroundColor: 'rgba(255, 59, 48, 0.85)', marginHorizontal: 16, borderRadius: 12, marginBottom: 8 },
  errorText: { color: '#ffffff', fontSize: 13, fontWeight: '600' },

  inputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: 'transparent',
    alignItems: 'center',
    gap: 8,
    top: 42,
  },
  input: {
    flex: 1,
    color: '#fff',
    backgroundColor: 'rgba(28, 28, 30, 0.75)',
    borderRadius: 22,
    paddingHorizontal: 18,
    fontSize: 15,
    height: 44,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  sendButton: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0A84FF',
    borderRadius: 22,
    paddingHorizontal: 18,
    height: 44,
    shadowColor: '#0A84FF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.5,
    shadowRadius: 4,
    elevation: 4,
  },
  sendButtonDisabled: { opacity: 0.45, backgroundColor: '#3a3a3c' },
  sendText: { color: '#ffffff', fontSize: 15, fontWeight: 'bold' },
});

