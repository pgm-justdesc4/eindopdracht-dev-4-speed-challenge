import time
from gpiozero import LED

# --- HARDWARE CONFIGURATIE (nieuw schema, zonder breadboard) ---
# Segmenten: A, B, C, D, E, F, G, DP
segments_pins = [19, 5, 24, 20, 21, 13, 22, 26]
# Digits: DIG1, DIG2, DIG3, DIG4
digit_pins = [25, 6, 12, 16]

# Initialisatie
segments = [LED(p) for p in segments_pins]
digits = [LED(p, active_high=False, initial_value=True) for p in digit_pins]

# Mapping van cijfers naar segmenten [A, B, C, D, E, F, G, DP]
num_map = {
    '0': [1, 1, 1, 1, 1, 1, 0, 0], '1': [0, 1, 1, 0, 0, 0, 0, 0],
    '2': [1, 1, 0, 1, 1, 0, 1, 0], '3': [1, 1, 1, 1, 0, 0, 1, 0],
    '4': [0, 1, 1, 0, 0, 1, 1, 0], '5': [1, 0, 1, 1, 0, 1, 1, 0],
    '6': [1, 0, 1, 1, 1, 1, 1, 0], '7': [1, 1, 1, 0, 0, 0, 0, 0],
    '8': [1, 1, 1, 1, 1, 1, 1, 0], '9': [1, 1, 1, 1, 0, 1, 1, 0],
    ' ': [0, 0, 0, 0, 0, 0, 0, 0]
}

def display_update(chars):
    """Toont de karakters en zet de punt op de juiste plek."""
    for i in range(4):
        char = chars[i]
        pattern = list(num_map.get(char, num_map[' ']))
        
        # Punt tussen seconden en honderdsten (positie 2 van links)
        if i == 2:
            pattern[7] = 1
            
        for d in digits: d.off()
        
        for j in range(8):
            if pattern[j] == 1:
                segments[j].on()
            else:
                segments[j].off()
        
        digits[i].on()
        time.sleep(0.001)

try:
    print("FINALE RACE TIMER GESTART!")
    print("Indeling: Seconden . Honderdsten")
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        secs = int(elapsed % 100)
        honds = int((elapsed * 100) % 100)
        
        time_str = f"{secs:02d}{honds:02d}"
        reversed_str = time_str[::-1]

        for _ in range(5):
            display_update(list(reversed_str))

except KeyboardInterrupt:
    print("\nTimer gestopt.")
    for d in digits: d.close()
    for s in segments: s.close()