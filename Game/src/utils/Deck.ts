export type Suit = 'Spades' | 'Hearts' | 'Diamonds' | 'Clubs';
export type Value = '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K' | 'A';

export interface CardType {
  id: string;
  suit: Suit;
  value: Value;
  color: 'red' | 'black';
}

export const SUITS: Suit[] = ['Spades', 'Hearts', 'Diamonds', 'Clubs'];
export const VALUES: Value[] = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

export const generateDeck = (): CardType[] => {
  const deck: CardType[] = [];
  for (const suit of SUITS) {
    for (const value of VALUES) {
      deck.push({
        id: `${value}-${suit}`,
        suit,
        value,
        color: (suit === 'Hearts' || suit === 'Diamonds') ? 'red' : 'black',
      });
    }
  }
  return deck;
};

export const shuffle = (deck: CardType[]): CardType[] => {
  const shuffled = [...deck];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
