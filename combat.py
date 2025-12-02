import random

class CombatResult:
    def __init__(self, message, player_dead=False, npc_dead=False, player_wounded=False, npc_wounded=False, player_staggered=False, npc_staggered=False):
        self.message = message
        self.player_dead = player_dead
        self.npc_dead = npc_dead
        self.player_wounded = player_wounded
        self.npc_wounded = npc_wounded
        self.player_staggered = player_staggered
        self.npc_staggered = npc_staggered

class CombatEngine:
    @staticmethod
    def player_attack(player, npc):
        # Canonical Zork: miss, wound, kill, stagger
        roll = random.random()
        if roll < 0.1:
            npc.health = 0
            npc.alive = False
            return CombatResult(f"You kill the {npc.name}!", npc_dead=True)
        elif roll < 0.7:
            npc.health -= 1
            if npc.health <= 0:
                npc.alive = False
                return CombatResult(f"You kill the {npc.name}!", npc_dead=True)
            return CombatResult(f"You wound the {npc.name}! (Health: {npc.health})", npc_wounded=True)
        elif roll < 0.85:
            return CombatResult(f"You stagger the {npc.name}!", npc_staggered=True)
        else:
            return CombatResult(f"You miss! The {npc.name} dodges.")

    @staticmethod
    def npc_attack(npc, player):
        roll = random.random()
        if roll < 0.1:
            player.health = 0
            return CombatResult(f"The {npc.name} kills you!", player_dead=True)
        elif roll < 0.7:
            player.health -= 1
            if player.health <= 0:
                return CombatResult(f"The {npc.name} kills you!", player_dead=True)
            return CombatResult(f"The {npc.name} wounds you! (Health: {player.health})", player_wounded=True)
        elif roll < 0.85:
            return CombatResult(f"The {npc.name} staggers you!", player_staggered=True)
        else:
            return CombatResult(f"The {npc.name} misses!")

    @staticmethod
    def combat_round(player, npc):
        # Player attacks first
        player_result = CombatEngine.player_attack(player, npc)
        messages = [player_result.message]
        if player_result.npc_dead:
            return '\n'.join(messages)
        # NPC attacks if alive
        npc_result = CombatEngine.npc_attack(npc, player)
        messages.append(npc_result.message)
        if npc_result.player_dead:
            return '\n'.join(messages)
        return '\n'.join(messages)
