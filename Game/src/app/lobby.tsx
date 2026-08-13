import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { connectSocket, sendSocketMessage, socket, setGlobalMessageHandler, setPlayerIndex, setRoomId as setGlobalRoomId } from '../utils/socket';

export default function LobbyScreen() {
  const { game, mode } = useLocalSearchParams();
  const [ipAddress, setIpAddress] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [roomId, setRoomId] = useState('');
  const [isWaiting, setIsWaiting] = useState(false);
  const [createdRoomId, setCreatedRoomId] = useState('');

  useEffect(() => {
    // If online mode, auto-connect to cloud server
    if (mode === 'online') {
      connectSocket(
        '9e009348-133d-4844-a65d-a2190c7e8745-00-3ajyej0s0gaq1.pike.replit.dev/ws',
        () => setIsConnected(true),
        (e) => Alert.alert("Error", "Could not connect to online server.")
      );
    } else if (socket && socket.readyState === WebSocket.OPEN) {
      setIsConnected(true);
    }
  }, [mode]);

  useEffect(() => {
    // Listen for messages from server
    setGlobalMessageHandler((data: any) => {
      if (data.type === 'ROOM_CREATED') {
        setCreatedRoomId(data.roomId);
        setIsWaiting(true);
        setGlobalRoomId(data.roomId);
        setPlayerIndex(data.playerIndex); // Host is 0
      }
      else if (data.type === 'GAME_START') {
        // Both players are in
        router.push(`/${game}`);
      }
      else if (data.type === 'JOINED_ROOM') {
        setGlobalRoomId(data.roomId);
        setPlayerIndex(data.playerIndex);
        // Wait for GAME_START if we need more players
        setIsWaiting(true); 
      }
      else if (data.type === 'ERROR') {
        Alert.alert("Error", data.message);
      }
    });
  }, [game]);

  const connectToServer = () => {
    if (!ipAddress) {
      Alert.alert("Error", "Please enter the Host Laptop IP Address");
      return;
    }
    
    connectSocket(
      ipAddress, 
      () => {
        setIsConnected(true);
      },
      (e) => {
        Alert.alert("Connection Failed", "Could not connect to the server at that IP.");
      }
    );
  };

  const createRoom = () => {
    sendSocketMessage({ type: 'CREATE_ROOM', game });
  };

  const joinRoom = () => {
    if (roomId.length !== 4) {
      Alert.alert("Invalid Room", "Room code must be 4 digits.");
      return;
    }
    sendSocketMessage({ type: 'JOIN_ROOM', roomId, game });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Lobby - {game}</Text>

      {!isConnected ? (
        <View style={styles.actionContainer}>
          <Text style={styles.infoText}>Enter Host Laptop IP Address</Text>
          <Text style={styles.subText}>(e.g. 192.168.1.5)</Text>
          <TextInput 
            style={styles.input}
            placeholder="192.168.x.x"
            placeholderTextColor="#ccc"
            value={ipAddress}
            onChangeText={setIpAddress}
          />
          <TouchableOpacity style={styles.button} onPress={connectToServer}>
            <Text style={styles.buttonText}>Connect</Text>
          </TouchableOpacity>
        </View>
      ) : isWaiting ? (
        <View style={styles.waitingContainer}>
          <Text style={styles.infoText}>Room Code:</Text>
          <Text style={styles.roomCode}>{createdRoomId || roomId}</Text>
          <Text style={styles.infoText}>Waiting for others to join...</Text>
        </View>
      ) : (
        <View style={styles.actionContainer}>
          <TouchableOpacity style={styles.button} onPress={createRoom}>
            <Text style={styles.buttonText}>Create New Room</Text>
          </TouchableOpacity>

          <Text style={styles.orText}>- OR -</Text>

          <TextInput 
            style={styles.input}
            placeholder="Enter 4-digit Code"
            placeholderTextColor="#ccc"
            keyboardType="number-pad"
            maxLength={4}
            value={roomId}
            onChangeText={setRoomId}
          />
          <TouchableOpacity style={[styles.button, styles.joinButton]} onPress={joinRoom}>
            <Text style={styles.buttonText}>Join Room</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#006400', alignItems: 'center', justifyContent: 'center', padding: 20 },
  title: { fontSize: 32, fontWeight: 'bold', color: 'white', marginBottom: 40, textTransform: 'capitalize' },
  actionContainer: { width: '100%', alignItems: 'center' },
  waitingContainer: { alignItems: 'center' },
  roomCode: { fontSize: 48, fontWeight: 'bold', color: '#FFD700', marginVertical: 20, letterSpacing: 5 },
  infoText: { fontSize: 18, color: 'white' },
  subText: { fontSize: 14, color: '#ccc', marginBottom: 15 },
  input: { width: '80%', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 10, padding: 15, fontSize: 24, color: 'white', textAlign: 'center', marginBottom: 15, borderWidth: 2, borderColor: 'white' },
  button: { backgroundColor: '#FFD700', paddingVertical: 15, paddingHorizontal: 40, borderRadius: 30, width: '80%', alignItems: 'center' },
  joinButton: { backgroundColor: '#8B4513' },
  buttonText: { fontSize: 20, fontWeight: 'bold', color: 'black' },
  orText: { color: 'white', fontSize: 16, marginVertical: 20 }
});
