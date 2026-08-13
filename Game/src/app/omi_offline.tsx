import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { CardType, generateDeck, shuffle, Suit } from '../utils/Deck';
import { Card } from '../components/Card';

const getOmiValue = (val: string) => {
  if (val === 'A') return 14;
  if (val === 'K') return 13;
  if (val === 'Q') return 12;
  if (val === 'J') return 11;
  return parseInt(val); // 7, 8, 9, 10
};

export default function OmiScreen() {
  const [players, setPlayers] = useState<CardType[][]>([[], [], [], []]);
  const [turn, setTurn] = useState<number>(1); // Player 2 starts initially
  const [trumpSuit, setTrumpSuit] = useState<Suit | null>(null);
  const [phase, setPhase] = useState<'trump_selection' | 'playing'>('trump_selection');
  
  const [currentTrick, setCurrentTrick] = useState<{player: number, card: CardType}[]>([]);
  const [leadingSuit, setLeadingSuit] = useState<Suit | null>(null);
  
  const [team1Tricks, setTeam1Tricks] = useState(0); // P1 & P3
  const [team2Tricks, setTeam2Tricks] = useState(0); // P2 & P4
  
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    initGame();
  }, []);

  const initGame = () => {
    let fullDeck = generateDeck();
    // Omi uses 32 cards (remove 2,3,4,5,6)
    let omiDeck = fullDeck.filter((c: CardType) => getOmiValue(c.value) >= 7);
    omiDeck = shuffle(omiDeck);

    // Deal 4 cards to everyone first
    let p1 = omiDeck.slice(0, 4);
    let p2 = omiDeck.slice(4, 8);
    let p3 = omiDeck.slice(8, 12);
    let p4 = omiDeck.slice(12, 16);
    
    // Store remaining to deal after trump selection
    const remaining = omiDeck.slice(16);

    setPlayers([p1, p2, p3, p4]);
    setTurn(1); // Player 2 picks trump
    setPhase('trump_selection');
    setTrumpSuit(null);
    setCurrentTrick([]);
    setLeadingSuit(null);
    setTeam1Tricks(0);
    setTeam2Tricks(0);
    setGameOver(false);
    
    // We'll store remaining in a ref or state to deal later
    // For simplicity in React, let's just deal all 8 right away but restrict UI
    p1 = omiDeck.slice(0, 8);
    p2 = omiDeck.slice(8, 16);
    p3 = omiDeck.slice(16, 24);
    p4 = omiDeck.slice(24, 32);
    
    const sortBySuitAndValue = (a: CardType, b: CardType) => {
      if (a.suit === b.suit) return getOmiValue(b.value) - getOmiValue(a.value);
      return a.suit > b.suit ? 1 : -1;
    };
    
    setPlayers([p1.sort(sortBySuitAndValue), p2.sort(sortBySuitAndValue), p3.sort(sortBySuitAndValue), p4.sort(sortBySuitAndValue)]);
  };

  const selectTrump = (suit: Suit) => {
    setTrumpSuit(suit);
    setPhase('playing');
    // Player 2 plays first card
  };

  const playCard = (card: CardType) => {
    // Validation
    if (currentTrick.length > 0 && card.suit !== leadingSuit) {
      // Must follow suit if they have it
      const hasSuit = players[turn].some(c => c.suit === leadingSuit);
      if (hasSuit) {
        Alert.alert("Invalid Play", `You must play a ${leadingSuit}`);
        return;
      }
    }

    const newPlayers = [...players];
    newPlayers[turn] = newPlayers[turn].filter((c: CardType) => c.id !== card.id);
    setPlayers(newPlayers);

    const newTrick = [...currentTrick, { player: turn, card }];
    setCurrentTrick(newTrick);

    if (newTrick.length === 1) {
      setLeadingSuit(card.suit);
    }

    if (newTrick.length === 4) {
      // Resolve trick
      setTimeout(() => resolveTrick(newTrick), 1500);
      setTurn(-1); // Wait state
    } else {
      setTurn((turn + 1) % 4);
    }
  };

  const resolveTrick = (trick: {player: number, card: CardType}[]) => {
    let winningCard = trick[0];
    
    for (let i = 1; i < 4; i++) {
      const current = trick[i];
      const winVal = getOmiValue(winningCard.card.value);
      const curVal = getOmiValue(current.card.value);
      
      if (current.card.suit === trumpSuit && winningCard.card.suit !== trumpSuit) {
        winningCard = current;
      } else if (current.card.suit === winningCard.card.suit && curVal > winVal) {
        winningCard = current;
      }
    }

    const winner = winningCard.player;
    if (winner === 0 || winner === 2) setTeam1Tricks((prev: number) => prev + 1);
    else setTeam2Tricks((prev: number) => prev + 1);

    setCurrentTrick([]);
    setLeadingSuit(null);
    setTurn(winner); // Winner leads next trick

    // Check game over
    if (players[winner].length === 0) {
      setGameOver(true);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Omi</Text>

      {/* Score Board */}
      <View style={styles.scoreBoard}>
        <Text style={styles.scoreText}>Team 1 (P1, P3): {team1Tricks} Tricks</Text>
        <Text style={styles.scoreText}>Team 2 (P2, P4): {team2Tricks} Tricks</Text>
        <Text style={styles.trumpText}>Trump: {trumpSuit || '?'}</Text>
      </View>
      
      {/* Table Area */}
      <View style={styles.centerArea}>
        {phase === 'trump_selection' ? (
          <View style={styles.trumpSelection}>
            <Text style={styles.statusText}>Player 2, select Trump!</Text>
            <View style={styles.suitButtons}>
              {['Spades', 'Hearts', 'Diamonds', 'Clubs'].map((s: any) => (
                <TouchableOpacity key={s} style={styles.suitBtn} onPress={() => selectTrump(s)}>
                  <Text style={styles.buttonText}>{s}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : gameOver ? (
          <View>
            <Text style={styles.statusText}>
              Game Over! {team1Tricks >= 5 ? 'Team 1 Wins!' : 'Team 2 Wins!'}
            </Text>
            <TouchableOpacity style={styles.restartBtn} onPress={initGame}>
              <Text style={styles.buttonText}>Play Again</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View>
             <Text style={styles.statusText}>
               {turn !== -1 ? `Player ${turn + 1}'s Turn` : 'Resolving trick...'}
             </Text>
             <View style={styles.trickContainer}>
               {currentTrick.map((t: any) => (
                 <View key={t.card.id} style={{ alignItems: 'center', margin: 5 }}>
                   <Text style={{ color: 'white', marginBottom: 5 }}>P{t.player + 1}</Text>
                   <Card card={t.card} />
                 </View>
               ))}
             </View>
          </View>
        )}
      </View>

      {/* Current Player's Hand */}
      {turn !== -1 && !gameOver && (
        <View style={styles.playerArea}>
          <Text style={styles.playerTitle}>Your Hand (Player {turn + 1})</Text>
          <ScrollView horizontal style={styles.handContainer}>
            {players[turn].map((card: CardType, i: number) => (
              <TouchableOpacity 
                key={card.id} 
                onPress={() => {
                  if (phase === 'playing') playCard(card);
                }}
                style={{ marginLeft: i === 0 ? 0 : -40 }}
              >
                <Card card={card} />
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#dc2626', // Red background for Omi
    paddingTop: 50,
    justifyContent: 'space-between',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  scoreBoard: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 10,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  scoreText: {
    color: 'white',
    fontWeight: 'bold',
  },
  trumpText: {
    color: '#fbbf24',
    fontWeight: 'bold',
  },
  centerArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  statusText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  trickContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  trumpSelection: {
    alignItems: 'center',
  },
  suitButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  suitBtn: {
    backgroundColor: '#3b82f6',
    padding: 15,
    borderRadius: 8,
  },
  restartBtn: {
    backgroundColor: '#10b981',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
  },
  playerArea: {
    padding: 20,
    backgroundColor: 'rgba(0,0,0,0.8)',
  },
  playerTitle: {
    color: 'white',
    marginBottom: 10,
    fontWeight: 'bold',
  },
  handContainer: {
    flexDirection: 'row',
    paddingVertical: 10,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  }
});
