const icons = ["🍒", "🍋", "🍇", "🍉", "⭐", "🌙", "🔥", "🌿"];
const board = document.getElementById("gameBoard");
const movesText = document.getElementById("moves");
const matchesText = document.getElementById("matches");
const totalPairsText = document.getElementById("totalPairs");
const message = document.getElementById("message");
const restartButton = document.getElementById("restartButton");

let firstCard = null;
let secondCard = null;
let lockBoard = false;
let moves = 0;
let matches = 0;

// 피셔-예이츠 셔플 알고리즘
function shuffle(items) {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
  }
  return shuffled;
}

// 카드 동적 생성
function createCard(icon) {
  const card = document.createElement("button");
  card.className = "card";
  card.type = "button";
  card.dataset.icon = icon;
  card.setAttribute("aria-label", "Hidden card");
  
  card.innerHTML = `
    <span class="card-inner">
      <span class="card-face card-back" aria-hidden="true"></span>
      <span class="card-face card-front" aria-hidden="true">${icon}</span>
    </span>
  `;
  
  card.addEventListener("click", () => flipCard(card));
  return card;
}

// 게임 시작 및 초기화
function startGame() {
  const deck = shuffle([...icons, ...icons]);
  
  firstCard = null;
  secondCard = null;
  lockBoard = false;
  moves = 0;
  matches = 0;
  
  movesText.textContent = moves;
  matchesText.textContent = matches;
  totalPairsText.textContent = icons.length;
  message.textContent = "";
  
  // 게임판 비우고 새로 만든 카드들 채워넣기
  board.replaceChildren(...deck.map(createCard));
}

// 카드 뒤집기 핸들러
function flipCard(card) {
  if (lockBoard || card === firstCard || card.classList.contains("matched")) return;
  
  card.classList.add("flipped");
  card.setAttribute("aria-label", `Revealed ${card.dataset.icon}`);
  
  if (!firstCard) {
    firstCard = card;
    return;
  }
  
  secondCard = card;
  moves += 1;
  movesText.textContent = moves;
  checkForMatch();
}

// 카드 일치 여부 확인
function checkForMatch() {
  if (firstCard.dataset.icon === secondCard.dataset.icon) {
    keepMatchedCards();
    return;
  }
  hideCards();
}

// 카드가 일치할 때 처리
function keepMatchedCards() {
  firstCard.classList.add("matched");
  secondCard.classList.add("matched");
  firstCard.disabled = true;
  secondCard.disabled = true;
  
  matches += 1;
  matchesText.textContent = matches;
  resetTurn();
  
  if (matches === icons.length) {
    message.textContent = `You won in ${moves} moves!`;
  }
}

// 카드가 일치하지 않을 때 처리 (다시 뒤집기)
function hideCards() {
  lockBoard = true;
  window.setTimeout(() => {
    firstCard.classList.remove("flipped");
    secondCard.classList.remove("flipped");
    firstCard.setAttribute("aria-label", "Hidden card");
    secondCard.setAttribute("aria-label", "Hidden card");
    resetTurn();
  }, 800);
}

// 턴 초기화
function resetTurn() {
  firstCard = null;
  secondCard = null;
  lockBoard = false;
}

// 이벤트 리스너 등록 및 게임 첫 실행
restartButton.addEventListener("click", startGame);
startGame();