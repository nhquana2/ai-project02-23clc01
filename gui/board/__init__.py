"""
Board module for Wumpus World visualization.

This module provides a modular rendering system with separate components for:
- ImageManager: Loading and scaling game images
- BackgroundRenderer: Rendering static background elements
- EntityRenderer: Rendering dynamic entities (agent, wumpus)
- KnowledgeRenderer: Rendering agent knowledge overlay
- BoardCompositor: Main coordinator that combines all layers

The Board class is an alias to BoardCompositor for backward compatibility.
"""

from .board_compositor import BoardCompositor

# Export Board as the main class for backward compatibility
Board = BoardCompositor

__all__ = ['Board', 'BoardCompositor']
