import React from 'react';
import { AvatarState } from '../domain/avatar_state';
import { RealisticAvatarComponent } from './RealisticAvatarRenderer';

export interface AvatarRendererProps {
  state: AvatarState;
}

export interface IAvatarRenderer {
  render(props: AvatarRendererProps): React.ReactNode;
}

/**
 * Photorealistic Character Avatar Renderer
 * Uses high-fidelity consistent portrait series with dynamic breathing and speaking pulses.
 */
export class RealisticAvatarRenderer implements IAvatarRenderer {
  render({ state }: AvatarRendererProps): React.ReactNode {
    return <RealisticAvatarComponent state={state} />;
  }
}

// Fallback / Legacy Static Emoji Renderer
export class StaticImageRenderer implements IAvatarRenderer {
  render({ state }: AvatarRendererProps): React.ReactNode {
    return <RealisticAvatarComponent state={state} />;
  }
}

