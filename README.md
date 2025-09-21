# 🃏 Advanced Card Game

A sophisticated multiplayer card game implemented in Python using Pygame, featuring advanced mechanics, AI opponents, and a modern staging system.

![Game Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎮 Game Features

### Core Gameplay
- **Card Staging System**: Stage multiple cards of the same rank before playing
- **"Finish Turn" Button**: Complete your turn after staging cards
- **Smart AI Opponent**: Computer player with strategic decision-making
- **Visual Effects**: Smooth animations and card transitions

### Advanced Mechanics
- **Special Card Effects**:
  - **6s**: Must be covered by the same player with another 6, same suit, or Jack
  - **7s**: Force opponents to draw cards (stackable)
  - **8s**: Skip opponent's turn and force them to draw
  - **Aces**: Skip opponent's turn (stackable)
  - **Jacks**: Change suit - choose any suit to continue with

### Enhanced Draw System
- **Smart Drawing**: Optional draws become forced if no playable cards
- **6-Covering Draws**: Multiple draws allowed when covering 6s
- **Draw Limits**: Maximum 1 draw per turn in normal gameplay

### Player Experience
- **Effect Indicators**: Visual feedback when players can't make moves
- **Suit Enforcement**: Clear indication of required suit after Jacks
- **Button Layout**: Intuitive bottom-left control panel
- **Card Visualization**: High-quality card images and smooth rendering

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Pygame library

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/card-game.git
cd card-game
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the game**:
```bash
python src/main.py
```

## 🎯 How to Play

1. **Starting**: Each player gets 5 cards from a standard deck
2. **Staging**: Click cards to stage them (same rank only)
3. **Playing**: Click "Finish Turn" to play staged cards
4. **Drawing**: Use "Draw Card" if you can't play (once per turn)
5. **Winning**: First player to empty their hand wins!

### Special Rules
- **6s Rule**: Only the player who played a 6 can cover it
- **Jack Effects**: Choose a new suit when playing Jacks
- **Stacking**: Play multiple cards of same rank together
- **Force Effects**: Some cards force draws or skips

## 🏗️ Project Structure

```
card-game/
├── src/
│   ├── main.py              # Game entry point
│   ├── game/
│   │   ├── card.py          # Card class implementation
│   │   ├── deck.py          # Deck management
│   │   ├── game.py          # Core game logic
│   │   └── player.py        # Player class
│   ├── gui/
│   │   ├── game_screen.py   # Main game interface
│   │   ├── menu_screen.py   # Menu system
│   │   ├── card_renderer.py # Card visualization
│   │   └── button.py        # UI components
│   └── images/              # Card graphics
├── tests/                   # Unit tests
├── test_*.py               # Integration tests
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🧪 Testing

The project includes comprehensive tests for all major components:

```bash
# Test all components
python test_effects.py
python test_suit_enforcement.py
python test_draw_mechanics.py
python test_six_covering_fix.py
python test_effect_indicators.py

# Run unit tests
pytest tests/
```

## 🎨 Technical Highlights

- **Modern Python**: Clean, well-documented code following PEP 8
- **Event-Driven Architecture**: Responsive UI with proper event handling
- **Modular Design**: Separated concerns with clear class responsibilities
- **Comprehensive Testing**: Full test coverage for game mechanics
- **Visual Polish**: Custom card renderer with smooth animations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Future Enhancements

- [ ] Multiplayer network support
- [ ] Card animation improvements
- [ ] Sound effects and music
- [ ] Tournament mode
- [ ] Custom deck themes
- [ ] Save/load game states

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Card images from public domain sources
- Pygame community for excellent documentation
- Contributors and testers who helped improve the game

---

**Enjoy the game!** 🎉