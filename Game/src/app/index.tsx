import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Link } from 'expo-router';

export default function Index() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sri Lankan Card Games</Text>
      
      <View style={styles.menu}>
        <Link href="/mode_select?game=omi" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Play Omi</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/mode_select?game=buruwa" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Play Buruwa</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/mode_select?game=higanna" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Play Higanna</Text>
          </TouchableOpacity>
        </Link>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e293b', // Dark slate background
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#f8fafc',
    marginBottom: 40,
    textAlign: 'center',
  },
  menu: {
    width: '100%',
    alignItems: 'center',
  },
  button: {
    backgroundColor: '#3b82f6',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    width: '80%',
    alignItems: 'center',
    marginBottom: 20,
  },
  disabledButton: {
    backgroundColor: '#475569',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
