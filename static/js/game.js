// Define the game board data (you'll need to replace this with your actual game data)
const gameBoard = [
    ['word1', 'word2', 'word3', 'word4', 'word5'],
    ['word6', 'word7', 'word8', 'word9', 'word10'],
    ['word11', 'word12', 'word13', 'word14', 'word15'],
    ['word16', 'word17', 'word18', 'word19', 'word20'],
    ['word21', 'word22', 'word23', 'word24', 'word25']
];

// Get the game board element from the HTML
const gameBoardElement = document.getElementById('game-board');

// Render the game board
function renderGameBoard() {
    let boardHTML = '';
    for (let row of gameBoard) {
        boardHTML += '<div class="row">';
        for (let word of row) {
            boardHTML += `<div class="word">${word}</div>`;
        }
        boardHTML += '</div>';
    }
    gameBoardElement.innerHTML = boardHTML;
}

// Call the renderGameBoard function to display the game board
renderGameBoard();