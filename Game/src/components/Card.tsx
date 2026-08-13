import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CardType } from '../utils/Deck';

const getSuitSymbol = (suit: string) => {
  switch (suit) {
    case 'Spades': return '♠';
    case 'Hearts': return '♥';
    case 'Diamonds': return '♦';
    case 'Clubs': return '♣';
    default: return '';
  }
};

interface CardProps {
  card: CardType | null; // if null, it's face down
  hidden?: boolean;
}

export const Card = ({ card, hidden = false }: CardProps) => {
  if (hidden || !card) {
    return (
      <View style={[styles.card, styles.cardBack]}>
        <Text style={styles.cardBackText}>🃏</Text>
      </View>
    );
  }

  const symbol = getSuitSymbol(card.suit);
  const color = card.color;

  return (
    <View style={styles.card}>
      <View style={styles.topLeft}>
        <Text style={[styles.value, { color }]}>{card.value}</Text>
        <Text style={[styles.suit, { color }]}>{symbol}</Text>
      </View>
      <View style={styles.center}>
        <Text style={[styles.bigSuit, { color }]}>{symbol}</Text>
      </View>
      <View style={styles.bottomRight}>
        <Text style={[styles.value, { color }]}>{card.value}</Text>
        <Text style={[styles.suit, { color }]}>{symbol}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    width: 80,
    height: 120,
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    margin: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
    padding: 4,
    justifyContent: 'space-between',
  },
  cardBack: {
    backgroundColor: '#208AEF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardBackText: {
    fontSize: 40,
  },
  topLeft: {
    alignItems: 'flex-start',
  },
  center: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  bottomRight: {
    alignItems: 'flex-end',
    transform: [{ rotate: '180deg' }],
  },
  value: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  suit: {
    fontSize: 14,
  },
  bigSuit: {
    fontSize: 32,
  },
});
