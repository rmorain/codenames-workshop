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
    }

    function handleCardClick(event) {
            const cardElement = event.target;
            const index = parseInt(cardElement.getAttribute('data-index'), 10);

            if (gameState.current_clue.number === 0) {
                alert("No more guesses allowed this turn.");
                return;
            }

            if (!gameState.guessed[index]) {
                gameState.guessed[index] = true;
                gameState.current_clue.number--; 

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

    socket.on('update', (data) => {
        gameState = data;
        renderGameBoard();
    });

    const gameBoardElement = document.getElementById('game-board');
    gameBoardElement.addEventListener('click', handleCardClick);

    renderGameBoard();
});
