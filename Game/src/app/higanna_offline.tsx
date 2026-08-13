import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { CardType, generateDeck, shuffle } from '../utils/Deck';
import { Card } from '../components/Card';

// Higanna Card Values: 3 is lowest, 2 is highest
const getValue = (val: string) => {
  if (val === '2') return 15;
  if (val === 'A') return 14;
  if (val === 'K') return 13;
  if (val === 'Q') return 12;
  if (val === 'J') return 11;
  return parseInt(val);
};

export default function HigannaScreen() {
  const [players, setPlayers] = useState<CardType[][]>([[], [], []]);
  const [turn, setTurn] = useState<number>(0);
  const [selectedCards, setSelectedCards] = useState<CardType[]>([]);
  
  const [currentTrick, setCurrentTrick] = useState<CardType[]>([]);
  const [lastPlayerToPlay, setLastPlayerToPlay] = useState<number | null>(null);
  
  const [winners, setWinners] = useState<number[]>([]);

  useEffect(() => {
    initGame();
  }, []);

  const initGame = () => {
    let deck = shuffle(generateDeck());
    let p1 = deck.slice(0, 18);
    let p2 = deck.slice(18, 35);
    let p3 = deck.slice(35, 52);

    // Sort hands by value
    const sortByValue = (a: CardType, b: CardType) => getValue(a.value) - getValue(b.value);
    p1.sort(sortByValue);
    p2.sort(sortByValue);
    p3.sort(sortByValue);

    setPlayers([p1, p2, p3]);
    setWinners([]);
    setCurrentTrick([]);
    setLastPlayerToPlay(null);
    setSelectedCards([]);
    
    // Player with 3 of Spades starts (simplified: Player 0 starts)
    setTurn(0);
  };

  const toggleSelectCard = (card: CardType) => {
    if (selectedCards.find(c => c.id === card.id)) {
      setSelectedCards(selectedCards.filter(c => c.id !== card.id));
    } else {
      setSelectedCards([...selectedCards, card]);
    }
  };

  const isValidPlay = (cards: CardType[]) => {
    if (cards.length === 0) return false;
    
    // Check if they are all same value (Single, Pair, Triple, Quad)
    const allSameValue = cards.every((c: CardType) => c.value === cards[0].value);
    
    // Check Sequence (e.g. 3,4,5 of same suit)
    cards.sort((a: CardType, b: CardType) => getValue(a.value) - getValue(b.value));
    const isSequence = cards.length >= 3 && 
                       cards.every((c: CardType) => c.suit === cards[0].suit) && 
                       cards.every((c: CardType, i: number) => i === 0 || getValue(c.value) === getValue(cards[i-1].value) + 1);

    if (!allSameValue && !isSequence) return false;

    // If starting a new trick, any valid combo is fine
    if (currentTrick.length === 0) return true;

    // If beating an existing trick
    if (cards.length !== currentTrick.length) return false;
    
    const currentTrickVal = getValue(currentTrick[0].value);
    const playVal = getValue(cards[0].value);
    
    return playVal > currentTrickVal;
  };

  const playCards = () => {
    if (!isValidPlay(selectedCards)) {
      Alert.alert("Invalid Play", "Your selected cards cannot beat the current trick.");
      return;
    }

    // Remove cards from current player
    const newPlayers = [...players];
    newPlayers[turn] = newPlayers[turn].filter((c: CardType) => !selectedCards.find((sc: CardType) => sc.id === c.id));
    setPlayers(newPlayers);

    setCurrentTrick(selectedCards);
    setLastPlayerToPlay(turn);
    setSelectedCards([]);

    checkWin(newPlayers);
  };

  const passTurn = () => {
    setSelectedCards([]);
    nextTurn();
  };

  const nextTurn = () => {
    let next = (turn + 1) % 3;
    
    // Skip players who have finished
    while (players[next].length === 0 && winners.length < 2) {
      next = (next + 1) % 3;
    }

    if (next === lastPlayerToPlay) {
      // Everyone passed, current player wins the trick
      setCurrentTrick([]);
      setLastPlayerToPlay(null);
    }
    
    setTurn(next);
  };

  const checkWin = (currentPlayers: CardType[][]) => {
    const newWinners = [...winners];
    if (currentPlayers[turn].length === 0 && !newWinners.includes(turn)) {
      newWinners.push(turn);
      setWinners(newWinners);
    }

    if (newWinners.length >= 2) {
      const higanna = [0, 1, 2].find((p: number) => !newWinners.includes(p));
      Alert.alert("Game Over!", `Raja: Player ${newWinners[0]+1}\nHiganna: Player ${higanna! + 1}`);
    } else {
      nextTurn();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Higanna</Text>
      
      {/* Current Trick Area */}
      <View style={styles.centerArea}>
        <Text style={styles.statusText}>
          {currentTrick.length > 0 ? `Current Trick to beat:` : `Start a new trick!`}
        </Text>
        <View style={styles.trickContainer}>
          {currentTrick.map((c: CardType) => <Card key={c.id} card={c} />)}
        </View>
        <Text style={styles.turnText}>Player {turn + 1}'s Turn</Text>
      </View>

      {/* Current Player's Hand */}
      <View style={styles.playerArea}>
        <ScrollView horizontal style={styles.handContainer}>
          {players[turn].map((card: CardType, i: number) => {
            const isSelected = selectedCards.find((c: CardType) => c.id === card.id);
            return (
              <TouchableOpacity 
                key={card.id} 
                onPress={() => toggleSelectCard(card)}
                style={{ marginLeft: i === 0 ? 0 : -40, marginTop: isSelected ? -20 : 0 }}
              >
                <Card card={card} />
              </TouchableOpacity>
            );
          })}
        </ScrollView>
        <View style={styles.buttonRow}>
          <TouchableOpacity style={[styles.actionButton, { backgroundColor: '#f43f5e' }]} onPress={passTurn}>
            <Text style={styles.buttonText}>Pass</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={playCards}>
            <Text style={styles.buttonText}>Play Selected</Text>
          </TouchableOpacity>
        </View>
      </View>

      {winners.length >= 2 && (
        <TouchableOpacity style={styles.restartButton} onPress={initGame}>
          <Text style={styles.buttonText}>Restart Game</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#8b5cf6', // Purple background
    paddingTop: 50,
    justifyContent: 'space-between',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 10,
  },
  centerArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.2)',
    padding: 20,
  },
  statusText: {
    color: 'white',
    fontSize: 16,
    marginBottom: 10,
  },
  turnText: {
    color: '#fbbf24',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
  },
  trickContainer: {
    flexDirection: 'row',
  },
  playerArea: {
    padding: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  handContainer: {
    flexDirection: 'row',
    paddingVertical: 20,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  actionButton: {
    backgroundColor: '#3b82f6',
    padding: 15,
    borderRadius: 8,
    flex: 0.45,
    alignItems: 'center',
  },
  restartButton: {
    backgroundColor: '#10b981',
    padding: 15,
    margin: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  }
});
