class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_card_info(self):
        rank_name = self.get_rank_name()
        return f"{rank_name} of {self.suit}"
        
    def get_rank_name(self):
        """Convert numeric rank to card name"""
        if self.rank == 1:
            return "Ace"
        elif self.rank == 11:
            return "Jack"
        elif self.rank == 12:
            return "Queen"
        elif self.rank == 13:
            return "King"
        else:
            return str(self.rank)