# Premium Frontend Implementation Plan

> **Goal**: Create a visually stunning, highly responsive, and robust frontend for Cognisphere using a modern "Premium" stack.

## 1. High-Level Architecture

We will build upon the foundation proposed by CTO.new (React 19 + Tailwind v4) but elevate it with libraries dedicated to **Interaction Design**, **Data Integrity**, and **Performance**.

### The "Antigravity Premium" Stack

| Layer | Technology | Reason for Upgrade |
|-------|------------|--------------------|
| **Core** | **React 19** | Latest features (Actions, useOptimistic). |
| **Styling** | **Tailwind CSS v4** + **Radix UI** | Unstyled, accessible primitives + high-performance atomic CSS. Allows for custom "Premium" design system. |
| **Animations** | **Framer Motion** | Complex layout animations, drag gestures, and smooth entry/exit transitions. Essential for "wow" factor. |
| **Data Fetching** | **TanStack Query (v5)** | Replaces simple Axios calls. Provides caching, auto-refetching, and **optimistic updates** (UI updates instantly before server responds). |
| **State** | **Zustand** | Kept for global client-state (e.g., UI preferences). |
| **Forms** | **React Hook Form** + **Zod** | Type-safe validation. Critical for complex forms like Profile or Ingestion. |
| **Visualization** | **D3.js** + **React Force Graph** | For the 3D/2D Knowledge Graph (already planned, but we will add glow effects and physics). |

## 2. Design Philosophy ("The Space Glass Aesthetic")

We will adopt a **"Space Glass"** theme matching the "Cognisphere" identity:
- **Glassmorphism**: Backdrop blur on panels (sidebars, modals).
- **Aurora Gradients**: Subtle, moving animated backgrounds in deep space colors (indigo, violet, slate).
- **Kinetic UI**:
    - Cards tilt slightly on hover.
    - Lists stagger-animate in.
    - Buttons have magnetic hover effects.

## 3. Component Architecture

### Core Layout (`Shell.tsx`)
- **Animated Sidebar**: Collapsible with spring physics.
- **Glass Header**: Sticky, blurs content behind it.
- **Micro-interactions**: Sound effects (optional, subtle) on critical actions.

### Feature Modules

#### A. Ingestion Engine
- **Drag & Drop Zone**: Animated particle effects when dragging files.
- **Progress Visualization**: Circular progress with liquid filling animation.

#### B. SRS Reviewer
- **Card Flip**: 3D transform animations.
- **Swipe Gestures**: Tinder-style swipe for Mobile/Touch screens using Framer Motion drag.
- **Spaced Repetition Feedback**: Confetti or glow bursts on "Easy" answers.

#### C. Knowledge Graph
- **Web User Interface**: Overlay HUD (Heads Up Display) style for graph controls.
- **Interactive Nodes**: Hovering a node dims unrelated nodes and highlights connections neon-bright.

#### D. Profile & Social
- **Data Viz**: Animated charts for mastery streaks.
- **Avatar**: Glowing borders based on "User Level" or "Streak".

## 4. Implementation Strategy

### Phase 1: Foundation (Days 1-2)
- [ ] Initialize Vite + React 19 + TypeScript.
- [ ] Configure Tailwind v4 with custom "Cognisphere" theme tokens.
- [ ] Set up TanStack Query provider and Axios interceptors.
- [ ] Create base UI primitives (Button, Card, Input) with Framer Motion wrapped.

### Phase 2: Core Experiences (Days 3-4)
- [ ] **Shell**: App layout with navigation.
- [ ] **Dashboard**: Grid layout with draggable widgets.
- [ ] **Ingestion**: File upload flow.

### Phase 3: Advanced Features (Days 5-6)
- [ ] **Knowledge Graph**: D3 integration.
- [ ] **Review Interface**: SRS logic + Animation.
- [ ] **Profile**: Forms and Charts.

## 5. Testing & Quality
- **E2E**: Cypress (Visual Regression Testing to ensure pixel perfection).
- **Unit**: Vitest + React Testing Library.
- **Mocking**: MSW (Mock Service Worker) to develop frontend without waiting for backend.

## 6. Communication with Backend
- We will strictly follow the TypeScript types defined in `SYNC_LOG.md`.
- We will use **Zod** schemas to validate API responses at runtime (defensive programming).
