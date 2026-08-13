import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { currentRoomId, myPlayerIndex, sendSocketMessage, setGlobalMessageHandler } from '../utils/socket';
import { CardType, generateDeck, shuffle } from '../utils/Deck';
import { Card } from '../components/Card';

type GameState = {
  p1Hand: CardType[];
  p2Hand: CardType[];
  discardPile: CardType[];
  turn: 1 | 2;
  gameOver: string | null;
};

export default function BuruwaScreen() {
  const [gameState, setGameState] = useState<GameState | null>(null);

  useEffect(() => {
    // Override global message handler to handle game state updates
    setGlobalMessageHandler((data: any) => {
      if (data.type === 'STATE_UPDATE') {
        setGameState({
          p1Hand: data.state.p1Hand || [],
          p2Hand: data.state.p2Hand || [],
          discardPile: data.state.discardPile || [],
          turn: data.state.turn,
          gameOver: data.state.gameOver || null
        });
      }
    });

    if (myPlayerIndex === 0 && !gameState) {
      // Host initializes the game
      initGame();
    }
  }, []);

  const initGame = () => {
    let deck = generateDeck();
    const jIndex = deck.findIndex((c: CardType) => c.value === 'J');
    if (jIndex > -1) deck.splice(jIndex, 1);

    deck = shuffle(deck);

    const half = Math.ceil(deck.length / 2);
    const p1 = deck.slice(0, half);
    const p2 = deck.slice(half);

    const initialState: GameState = {
      p1Hand: p1,
      p2Hand: p2,
      discardPile: [],
      turn: 1,
      gameOver: null
    };

    syncState(initialState);
  };

  const syncState = (newState: Partial<GameState>) => {
    sendSocketMessage({ type: 'UPDATE_STATE', roomId: currentRoomId, state: newState });
  };

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
    if (!gameState) return;
    let currentDiscard = [...gameState.discardPile];
    
    if (myPlayerIndex === 0) {
      const p1Result = discardPairs(gameState.p1Hand, currentDiscard);
      syncState({ p1Hand: p1Result.newHand, discardPile: p1Result.newDiscard });
    } else {
      const p2Result = discardPairs(gameState.p2Hand, currentDiscard);
      syncState({ p2Hand: p2Result.newHand, discardPile: p2Result.newDiscard });
    }
  };

  const drawCardFromOpponent = (cardIndex: number) => {
    if (!gameState) return;
    
    if ((myPlayerIndex === 0 && gameState.turn !== 1) || (myPlayerIndex === 1 && gameState.turn !== 2)) {
      return;
    }

    const isP1Turn = gameState.turn === 1;
    const fromHand = isP1Turn ? [...gameState.p2Hand] : [...gameState.p1Hand];
    const toHand = isP1Turn ? [...gameState.p1Hand] : [...gameState.p2Hand];

    const drawnCard = fromHand[cardIndex];
    fromHand.splice(cardIndex, 1);
    toHand.push(drawnCard);

    const result = discardPairs(toHand, gameState.discardPile);

    let gameOver = null;
    if (isP1Turn && result.newHand.length === 0) gameOver = "Player 1 Wins!";
    if (!isP1Turn && result.newHand.length === 0) gameOver = "Player 2 Wins!";

    syncState({
      [isP1Turn ? 'p1Hand' : 'p2Hand']: result.newHand,
      [isP1Turn ? 'p2Hand' : 'p1Hand']: fromHand,
      discardPile: result.newDiscard,
      turn: isP1Turn ? 2 : 1,
      gameOver
    });
  };

  if (!gameState) {
    return <View style={styles.container}><Text style={styles.title}>Loading game state...</Text></View>;
  }

  const myHand = myPlayerIndex === 0 ? gameState.p1Hand : gameState.p2Hand;
  const oppHand = myPlayerIndex === 0 ? gameState.p2Hand : gameState.p1Hand;
  const isMyTurn = (myPlayerIndex === 0 && gameState.turn === 1) || (myPlayerIndex === 1 && gameState.turn === 2);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Buruwa (Room {currentRoomId}) - You are P{myPlayerIndex + 1}</Text>
      
      {/* Opponent Area */}
      <View style={styles.playerArea}>
        <Text style={styles.playerText}>Opponent (Cards: {oppHand.length})</Text>
        <ScrollView horizontal style={styles.handContainer}>
          {oppHand.map((card: CardType, i: number) => (
            <TouchableOpacity 
              key={card.id} 
              style={{ marginLeft: i === 0 ? 0 : -50 }}
              disabled={!isMyTurn}
              onPress={() => drawCardFromOpponent(i)}
            >
              <Card card={card} hidden={true} /> 
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Center Area */}
      <View style={styles.centerArea}>
        <TouchableOpacity style={styles.actionButton} onPress={performInitialDiscard}>
          <Text style={styles.buttonText}>Initial Discard (Pair Remove)</Text>
        </TouchableOpacity>
        
        {!gameState.gameOver && (
          <Text style={styles.turnText}>
            {isMyTurn ? "Your Turn! Pick a card from opponent." : "Waiting for opponent..."}
          </Text>
        )}

        <Text style={styles.discardText}>Discard Pile: {gameState.discardPile.length} cards</Text>

        {gameState.gameOver && (
          <View style={styles.gameOverContainer}>
            <Text style={styles.gameOverText}>{gameState.gameOver}</Text>
            {myPlayerIndex === 0 && (
              <TouchableOpacity style={styles.actionButton} onPress={initGame}>
                <Text style={styles.buttonText}>Play Again</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>

      {/* My Area */}
      <View style={styles.playerArea}>
        <Text style={styles.playerText}>Your Hand (Cards: {myHand.length})</Text>
        <ScrollView horizontal style={styles.handContainer}>
          {myHand.map((card: CardType, i: number) => (
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
  turnText: { color: 'white', fontSize: 18, fontWeight: 'bold', marginVertical: 10 },
  discardText: { color: 'white', marginTop: 10 },
  gameOverContainer: { alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.8)', padding: 20, borderRadius: 10, marginTop: 20 },
  gameOverText: { color: '#fbbf24', fontSize: 20, fontWeight: 'bold', marginBottom: 15 }
});
