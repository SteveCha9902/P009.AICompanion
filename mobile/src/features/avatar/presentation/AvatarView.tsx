import React, { Component, ErrorInfo, useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AvatarState } from '../domain/avatar_state';
import { avatarService } from '../services/avatar_service';
import { RealisticAvatarRenderer } from './AvatarRenderer';


// Error Boundary to ensure Avatar failure doesn't crash Conversation/Voice
interface ErrorBoundaryProps {
  children: React.ReactNode;
}
interface ErrorBoundaryState {
  hasError: boolean;
}

class AvatarErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(_: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Avatar Rendering Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Avatar Offline</Text>
        </View>
      );
    }
    return this.props.children;
  }
}

// AvatarView Component
export const AvatarView: React.FC = () => {
  const [avatarState, setAvatarState] = useState<AvatarState | null>(null);

  useEffect(() => {
    // Subscribe to AvatarService for merged real-time + semantic updates
    const unsubscribe = avatarService.subscribe((state) => {
      setAvatarState(state);
    });
    return () => unsubscribe();
  }, []);

  if (!avatarState) {
    return <View style={styles.container}><Text>Loading Avatar...</Text></View>;
  }

  // Instantiate the realistic avatar renderer
  const renderer = new RealisticAvatarRenderer();


  return (
    <AvatarErrorBoundary>
      <View style={styles.container}>
        {renderer.render({ state: avatarState })}
      </View>
    </AvatarErrorBoundary>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#333333',
  },

  errorText: {
    color: '#FF6B6B',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
