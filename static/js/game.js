document.addEventListener('DOMContentLoaded', function() {
    function renderGameBoard() {
        let boardHTML = '';
        for (let row = 0; row < 5; row++) {
            boardHTML += '<div class="row">';

            for (let col = 0; col < 5; col++) {
                const index = row * 5 + col;
                const color = gameState.colors[index];
                const word = gameState.words[index];
                const isGuessed = gameState.guessed[index];

                let cardClass = 'word';
                let cardContent = word;

                if (isGuessed) {
                    cardClass += ` ${color.toLowerCase()}`;
                    cardContent = '';
                }

                boardHTML += `<div class="${cardClass}" data-index="${index}">${cardContent}</div>`;
            }

            boardHTML += '</div>';
        }
        const gameBoardElement = document.getElementById('game-board');
        gameBoardElement.innerHTML = boardHTML;

        const currentTurnElement = document.getElementById('current-turn');
        currentTurnElement.textContent = `Current Turn: ${gameState.current_turn}`;

        const currentClueElement = document.getElementById('current-clue');
        const clueWord = gameState.current_clue.word;
        const clueNumber = gameState.current_clue.number;
        currentClueElement.textContent = `Current Clue: ${clueWord} (${clueNumber})`;

        const guessesRemainingElement = document.getElementById('guesses-remaining');
        guessesRemainingElement.textContent = `Guesses remaining: ${gameState.guesses_remaining}`;

        const teamRoleElement = document.getElementById('team-role');
        teamRoleElement.textContent = `Team: ${playerTeam} Role: ${playerRole}`;

    }

    function handleCardClick(event) {
            const cardElement = event.target;
            const index = parseInt(cardElement.getAttribute('data-index'), 10);


            if (!gameState.guessed[index]) {
                const currentGuess = index;
                if (gameState.current_turn != playerTeam){
                    alert("Not your turn!");
                    return;
                }

                if (playerRole != "guesser"){
                    alert("You are not the guesser!");
                    return;
                }

                if (gameState.guesses_remaining === 0) {
                    alert("No more guesses allowed this turn.");
                    return;
                }
                gameState.guessed[index] = true;
                gameState.guesses_remaining--; 

                fetch('/update_game_state', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({gameState, currentGuess})
                })
                .then(response => response.json())
                .then(data => {
                    gameState = data;
                    renderGameBoard();
                })
                .catch(error => console.error('Error:', error));
            }
    }

    // Function to handle clue submission
    function handleClueSubmission() {
        if (gameState.current_turn != playerTeam){
            alert("Not your turn!");
            return;
        }

        if (playerRole != "spymaster"){
            alert("You are not the spymaster!");
            return;
        }
        const clueWordInput = document.getElementById('clue-word');
        const clueNumberInput = document.getElementById('clue-number');

        const newClueWord = clueWordInput.value.trim();
        const newClueNumber = parseInt(clueNumberInput.value, 10);

        if (newClueWord && !isNaN(newClueNumber)) {
            gameState.current_clue.word = newClueWord;
            gameState.current_clue.number = newClueNumber;
            gameState.guesses_remaining = newClueNumber;

            // Clear the input fields
            clueWordInput.value = '';
            clueNumberInput.value = '';
            fetch('/update_game_state', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gameState)
            })
            .then(response => response.json())
            .then(data => {
                gameState = data;
                renderGameBoard();
            })
            .catch(error => console.error('Error:', error));
        }

    }

    const socket = io()
    socket.on('connect', () => {
            console.log('Connected to the server');
        });
    socket.on('player_info', (data) => {
            console.log('Player Info:', data);
        });

    socket.on('update', (data) => {
        gameState = data;
        renderGameBoard();
    });

    const gameBoardElement = document.getElementById('game-board');
    gameBoardElement.addEventListener('click', handleCardClick);

    // Add event listener for the "Submit Clue" button
    if (playerRole == "spymaster"){
        const submitClueButton = document.getElementById('submit-clue');
        submitClueButton.addEventListener('click', handleClueSubmission);
    }
    renderGameBoard();
});
