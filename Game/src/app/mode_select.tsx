import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';

export default function ModeSelectScreen() {
  const { game } = useLocalSearchParams();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select Game Mode</Text>
      <Text style={styles.subtitle}>Game: {game}</Text>

      <View style={styles.menu}>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => router.push(`/${game}_offline`)}
        >
          <Text style={styles.buttonText}>🧍 Offline (Pass & Play)</Text>
          <Text style={styles.descText}>Play on a single phone</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.button}
          onPress={() => router.push(`/lobby?game=${game}&mode=hotspot`)}
        >
          <Text style={styles.buttonText}>📡 Local Hotspot</Text>
          <Text style={styles.descText}>Play with friends next to you</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.button}
          onPress={() => router.push(`/lobby?game=${game}&mode=online`)}
        >
          <Text style={styles.buttonText}>🌍 Global Online</Text>
          <Text style={styles.descText}>Play over the internet</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#8B4513',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFD700',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 20,
    color: 'white',
    marginBottom: 40,
    textTransform: 'capitalize'
  },
  menu: {
    width: '100%',
    alignItems: 'center',
  },
  button: {
    backgroundColor: '#3b82f6',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 30,
    width: '80%',
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  descText: {
    color: '#e2e8f0',
    fontSize: 14,
  }
});
