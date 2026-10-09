import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { HomeScreen } from '../screens/HomeScreen';
import { ConversationScreen } from '../screens/ConversationScreen';
import { MemoriesScreen } from '../screens/MemoriesScreen';
import { RelationshipScreen } from '../screens/RelationshipScreen';
import { SettingsScreen } from '../screens/SettingsScreen';
import { CharacterTabScreen } from './CharacterTabScreen';
import { CompanionScreen } from '../screens/CompanionScreen';
import { SharedStoryScreen } from '../screens/SharedStoryScreen';

const Tab = createBottomTabNavigator();

const TAB_ICONS: Record<string, string> = {
  Companion: '✨',
  Character: '🎭',
  Memories: '🧠',
  Relationship: '💖',
  Settings: '⚙️',
};

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarStyle: {
            backgroundColor: '#121212',
            borderTopColor: '#2A2A2A',
            height: 96,
            paddingBottom: 40,
            paddingTop: 8,
          },
          tabBarItemStyle: {
            flex: 1,
            alignItems: 'center',
            justifyContent: 'center',
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: '#888888',
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: '600',
            marginTop: 2,
          },
          tabBarIcon: ({ focused }) => {
            const icon = TAB_ICONS[route.name] || '📱';
            return (
              <Text
                style={{
                  fontSize: focused ? 22 : 20,
                  opacity: focused ? 1 : 0.6,
                  transform: [{ scale: focused ? 1.08 : 1.0 }]
                }}
              >
                {icon}
              </Text>
            );
          },
        })}
      >
        <Tab.Screen name="Companion" component={CompanionScreen} options={{ tabBarLabel: '아바타' }} />
        <Tab.Screen name="Character" component={CharacterTabScreen} options={{ tabBarLabel: '캐릭터' }} />
        <Tab.Screen name="Memories" component={MemoriesScreen} options={{ tabBarLabel: '기억' }} />
        <Tab.Screen name="Relationship" component={RelationshipScreen} options={{ tabBarLabel: '관계' }} />
        <Tab.Screen name="Settings" component={SettingsScreen} options={{ tabBarLabel: '설정' }} />
        <Tab.Screen
          name="SharedStory"
          component={SharedStoryScreen}
          options={{ 
            tabBarItemStyle: { display: 'none' },
            tabBarButton: () => null 
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}


