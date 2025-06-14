#in many games like FF, of LoH I mentioned in the brief description, the story basically is a sort of a spreadsheet.
#I use similar approach for dialog structuring, which is very scalable.
#can easily be extended with char portraits to be shown in a dialog box, different sprites animations, etc.

dialog_sequences = {
    # opening dialog at the game start
    "intro": [
        {"name": "", "text": "The Barren Plateau, northeast of the ruins of the once-glorious capital city of Ersten. The hand on the unusually shaped chronometer hanging from the mage’s belt was steadily nearing zero. There was almost no time left."},
        {"name": "Archenemy", "text": "You managed to cross the Garden-Where-Nothing-Dies, Mage. Impressive. I left that place loop-locked, with a proper guardian... yet you emerged. You have my praise."},
        {"name": "Mage", "text": "I do not need praise from you or your kind. That garden... it... No. All of that means nothing. Your deeds will end here and now."},
        {"name": "Archenemy", "text": "Is that why you came here? Or are you seeking answers? Why I unbound the Seals? Why I gathered all that energy? Why the skies burn red and the Moon bleeds? No... you still don’t understand. This isn’t cause and effect. It’s superposition. I was always your enemy - and never."},
        {"name": "Archenemy", "text": "That night in the capital... we both lost something valuable."},
        {"name": "Archenemy", "text": "The Moon - surely you’ve felt it before. The energy it drains from the world is just a catalyst. A catalyst for..."},
        {"name": "Mage", "text": "Enough! You’ve fooled enough people. You broke the Third Seal, manipulated the king... And now you’re just trying to buy yourself time."},
        {"name": "Mage", "text": "Your time in this world has finally come to an end."},
        {"name": "Archenemy", "text": "So be it. Yet the world is just a probability. I can see through it. You being here is a measurement error, Mage."},
        {"name": "Archenemy", "text": "Do you really think you can stand against me?"},
        {"name": "", "text": "The Archenemy barely moved, but the sudden burst of energy was palpable in the air."},
        {"name": "", "text": "Suddenly, a strange voice filled the Mage's ears."},
        {"name": "???", "text": "She thinks you'll lose anyway, Mage. Oh, why so surprised? Have you already forgotten me? What a pity... your memory is still fractured. I wonder how you made it this far without it. Seems I have no choice but to remind you."},
        {"name": "???", "text": "Evaluation of |00> will do nothing for you. |01> is an attack, |10> is a defense spell, and |11> will heal you."},
        {"name": "???", "text": "Anyway, for now, she can use only I, H, and X gates, and the measurement of the results will occur each turn. Remember, your action is defined by the leftmost two values of the state after measuring. Her side is right."},
        {"name": "???", "text": "Good luck, Mage. You'll need it."}
    ],

    # final dialog when the battle is successfully won
    "final": [
        {"name": "Archenemy", "text": "This... outcome was not... in any of my projections. I see. I see it now. All branches burn... in the end. You've only delayed it... Death is just another... measurement..."},
        {"name": "???", "text": "You did a good job, Mage. We will not meet again. Farewell, Mage..."},
        {"name": "", "text": "The skies have cleared, and the strange voice has faded away completely. You have a feeling that you are missing something important here."},
        {"name": "", "text": "The hand on the chronometer has finally frozen."},
        {"name": "Mage", "text": "The evil aura is gone, yet the crack on the moon... Hmmm. It seems there's still a lot of work left to do."},
        {"name": "Mage", "text": "Now... what size of band-aid does it take to patch up a moon?"},
    ],

    
    # dialog when the boss enters the phase 2
    "phase2": [
        {"name": "Archenemy", "text": "Your quantum magic is adorable - like a child playing chess with a god."},
        {"name": "", "text": "The Archenemy channeled magical power and cast an uncanny spell."},
        {"name": "", "text": "The X-gate for the Mage is now sealed."},
        {"name": "???", "text": "The enemy can now use the X, H, Z, and CNOT gates. Her attacks are growing stronger. Measurement will occur each two turns. Hold on, Mage - I have faith in you."}
    ],

    # dialog when the boss enters the phase 3
    "phase3": [
        {"name": "Archenemy", "text": "No more games! Now you face my true power!"},
        {"name": "", "text": "The Archenemy channeled magical power and cast an uncanny spell."},
        {"name": "", "text": "The H-gate for the Mage is now sealed."},
        {"name": "???", "text": "Now she can use the X, H, Z, T, RX, RY, RZ, and CCNOT gates. Her attacks are becoming even stronger - but she pays a price. Her body won’t withstand that much power for long. Your attacks are stronger now as well. Measurement will occur each three turns from now on."},
    ],

    # final dialog when the player has lost
    "game_lost": [
        {"name": "Archenemy", "text": "As if there could be any other outcome. The prophecy will be fulfilled, and your body will serve as a fine vessel."},
        {"name": "", "text": "The Mage has fallen. The flames of hope are extinguished. The world fades into quantum noise..."},
        {"name": "", "text": "The fates of the others, however, are..."},
        {"name": "", "text": "The hand on the chronometer reached zero."},
    ]

}





