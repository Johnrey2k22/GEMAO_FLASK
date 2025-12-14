#!/usr/bin/env python3
"""
Game Launcher - Bridges web interface with Python games (Tkinter/Pygame)
Launches games in a controlled subprocess and captures scores.
"""

import sys
import os
import subprocess
import re  # IMPORT ADDED: For smarter score extraction

class GameLauncher:
    def __init__(self, game_file_path, timeout=300):
        self.game_file_path = game_file_path
        self.timeout = timeout
        
    def launch_game(self):
        """Launch the game and return the score"""
        try:
            # Execute the game as subprocess to handle imports correctly
            # Note: sys.executable ensures we use the same python interpreter
            result = subprocess.run(
                [sys.executable, self.game_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(self.game_file_path),
                shell=False
            )
            
            # Extract score from stdout
            score = self._extract_score_from_output(result.stdout)
            
            return {
                'success': True,
                'score': score,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Game timed out',
                'score': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'score': 0
            }
    
    def _extract_score_from_output(self, output):
        """
        Extract score from stdout. 
        Enhanced version: Looks for FINAL_SCORE marker first, then fallback to generic digit extraction.
        """
        try:
            # Look for explicit FINAL_SCORE marker first
            score_match = re.search(r'FINAL_SCORE:(\d+)', output)
            if score_match:
                return int(score_match.group(1))
            
            # Fallback: Find all sequences of digits in the output
            # r'\d+' looks for one or more digits
            numbers = re.findall(r'\d+', output)
            
            if numbers:
                # Return the last number found (usually the final score)
                return int(numbers[-1])
                
        except (ValueError, AttributeError):
            pass
        return 0

def main():
    """Command line interface for the launcher"""
    if len(sys.argv) != 2:
        print("Usage: python game_launcher.py <game_file_path>", file=sys.stderr)
        sys.exit(1)
    
    game_file_path = sys.argv[1]
    
    # Validate file exists
    if not os.path.exists(game_file_path):
        print(f"Game file not found: {game_file_path}", file=sys.stderr)
        sys.exit(1)
    
    # Launch game
    launcher = GameLauncher(game_file_path)
    result = launcher.launch_game()
    
    if result['success']:
        print(result['score'])  # Print just the score for upstream capture
        sys.exit(0)
    else:
        print(f"Game failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()