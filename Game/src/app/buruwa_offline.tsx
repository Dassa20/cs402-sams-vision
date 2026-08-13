import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { CardType, generateDeck, shuffle } from '../utils/Deck';
import { Card } from '../components/Card';

export default function BuruwaOfflineScreen() {
  const [player1, setPlayer1] = useState<CardType[]>([]);
  const [player2, setPlayer2] = useState<CardType[]>([]);
  const [discardPile, setDiscardPile] = useState<CardType[]>([]);
  const [turn, setTurn] = useState<1 | 2>(1); // 1 = P1 pulls from P2, 2 = P2 pulls from P1
  const [gameOver, setGameOver] = useState<string | null>(null);

  const initGame = () => {
    let deck = generateDeck();
    const jIndex = deck.findIndex((c: CardType) => c.value === 'J');
    if (jIndex > -1) deck.splice(jIndex, 1);
    deck = shuffle(deck);

    const half = Math.ceil(deck.length / 2);
    setPlayer1(deck.slice(0, half));
    setPlayer2(deck.slice(half));
    setDiscardPile([]);
    setTurn(1);
    setGameOver(null);
  };

  useEffect(() => { initGame(); }, []);

  const discardPairs = (hand: CardType[], currentDiscard: CardType[]) => {
    let newHand = [...hand];
    let newDiscard = [...currentDiscard];
    let foundPair = true;

    while (foundPair) {
      foundPair = false;
      const valuesCount: { [key: string]: number[] } = {};
      
      for (let i = 0; i < newHand.length; i++) {
        const val = newHand[i].value;
        if (!valuesCount[val]) valuesCount[val] = [];
        valuesCount[val].push(i);
      }

      for (const val in valuesCount) {
        if (valuesCount[val].length >= 2) {
          const idx1 = valuesCount[val][0];
          const idx2 = valuesCount[val][1];
          newDiscard.push(newHand[idx1], newHand[idx2]);
          newHand.splice(Math.max(idx1, idx2), 1);
          newHand.splice(Math.min(idx1, idx2), 1);
          foundPair = true;
          break; 
        }
      }
    }
    return { newHand, newDiscard };
  };

  const performInitialDiscard = () => {
    let currentDiscard = [...discardPile];
    const p1Result = discardPairs(player1, currentDiscard);
    const p2Result = discardPairs(player2, p1Result.newDiscard);
    setPlayer1(p1Result.newHand);
    setPlayer2(p2Result.newHand);
    setDiscardPile(p2Result.newDiscard);
  };

  const drawCard = (fromPlayer: CardType[], toPlayer: CardType[], setFrom: any, setTo: any) => {
    if (fromPlayer.length === 0) return;
    const randomIndex = Math.floor(Math.random() * fromPlayer.length);
    const drawnCard = fromPlayer[randomIndex];
    
    const newFrom = [...fromPlayer];
    newFrom.splice(randomIndex, 1);

    const newTo = [...toPlayer, drawnCard];
    const result = discardPairs(newTo, discardPile);

    setFrom(newFrom);
    setTo(result.newHand);
    setDiscardPile(result.newDiscard);
  };

  const handleTurn = () => {
    if (turn === 1) {
      drawCard(player2, player1, setPlayer2, setPlayer1);
      setTurn(2);
    } else {
      drawCard(player1, player2, setPlayer1, setPlayer2);
      setTurn(1);
    }
  };

  useEffect(() => {
    if (player1.length === 0 && player2.length > 0) setGameOver("Player 1 Wins! Player 2 is the Buruwa!");
    else if (player2.length === 0 && player1.length > 0) setGameOver("Player 2 Wins! Player 1 is the Buruwa!");
  }, [player1, player2]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Buruwa (Offline)</Text>
      
      <View style={styles.playerArea}>
        <Text style={styles.playerText}>Player 2 (Cards: {player2.length})</Text>
        <ScrollView horizontal style={styles.handContainer}>
          {player2.map((card: CardType, i: number) => (
            <View key={card.id} style={{ marginLeft: i === 0 ? 0 : -50 }}>
              <Card card={card} hidden={false} />
            </View>
          ))}
        </ScrollView>
      </View>

      <View style={styles.centerArea}>
        <TouchableOpacity style={styles.actionButton} onPress={performInitialDiscard}>
          <Text style={styles.buttonText}>Initial Discard</Text>
        </TouchableOpacity>
        
        {!gameOver && (
          <TouchableOpacity style={styles.actionButton} onPress={handleTurn}>
            <Text style={styles.buttonText}>{turn === 1 ? "P1 Draw from P2" : "P2 Draw from P1"}</Text>
          </TouchableOpacity>
        )}

        <Text style={styles.discardText}>Discard Pile: {discardPile.length} cards</Text>

        {gameOver && (
          <View style={styles.gameOverContainer}>
            <Text style={styles.gameOverText}>{gameOver}</Text>
            <TouchableOpacity style={styles.actionButton} onPress={initGame}>
              <Text style={styles.buttonText}>Play Again</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      <View style={styles.playerArea}>
        <Text style={styles.playerText}>Player 1 (Cards: {player1.length})</Text>
        <ScrollView horizontal style={styles.handContainer}>
          {player1.map((card: CardType, i: number) => (
            <View key={card.id} style={{ marginLeft: i === 0 ? 0 : -50 }}>
              <Card card={card} hidden={false} />
            </View>
          ))}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#10b981', paddingTop: 50, justifyContent: 'space-between' },
  title: { fontSize: 24, fontWeight: 'bold', color: 'white', textAlign: 'center', marginBottom: 10 },
  playerArea: { flex: 1, padding: 10 },
  playerText: { color: 'white', fontWeight: 'bold', marginBottom: 5 },
  handContainer: { flexDirection: 'row', padding: 10 },
  centerArea: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.2)' },
  actionButton: { backgroundColor: '#3b82f6', padding: 12, borderRadius: 8, marginVertical: 5 },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  discardText: { color: 'white', marginTop: 10 },
  gameOverContainer: { alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.8)', padding: 20, borderRadius: 10, marginTop: 20 },
  gameOverText: { color: '#fbbf24', fontSize: 20, fontWeight: 'bold', marginBottom: 15 }
});
