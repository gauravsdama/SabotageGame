"use strict";

const setupStep = document.querySelector("#setup-step");
const gameGrid = document.querySelector("#game-grid");
const lobbyStep = document.querySelector("#lobby-step");
const roleStep = document.querySelector("#role-step");
const taskStep = document.querySelector("#task-step");
const voteStep = document.querySelector("#vote-step");
const resultStep = document.querySelector("#result-step");
const phase = document.querySelector("#phase");
const playerList = document.querySelector("#players");
const voteSelect = document.querySelector("#vote");
const startGame = document.querySelector("#start-game");

let players = [];
let sabotages = 0;

function roomCode() {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const values = crypto.getRandomValues(new Uint8Array(6));
  return Array.from(values, (value) => alphabet[value % alphabet.length]).join("");
}

function renderPlayers() {
  playerList.replaceChildren(
    ...players.map((player, index) => {
      const item = document.createElement("li");
      const number = document.createElement("span");
      const name = document.createElement("strong");
      const state = document.createElement("small");
      number.textContent = String(index + 1);
      name.textContent = player;
      state.textContent = index === 0 ? "Host" : "Joined";
      item.append(number, name, state);
      return item;
    }),
  );

  voteSelect.replaceChildren(
    ...players.map((player, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = player;
      return option;
    }),
  );

  startGame.disabled = players.length < 2;
}

document.querySelector("#create-room-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const host = new FormData(event.currentTarget).get("hostName").trim();
  if (!host) return;

  players = [host];
  document.querySelector("#room-code").textContent = roomCode();
  setupStep.hidden = true;
  gameGrid.hidden = false;
  renderPlayers();
  document.querySelector("#player-name").focus();
});

document.querySelector("#join-room-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const input = form.elements.playerName;
  const player = input.value.trim();
  if (!player || players.some((name) => name.toLowerCase() === player.toLowerCase())) return;

  players.push(player);
  renderPlayers();
  form.reset();
});

startGame.addEventListener("click", () => {
  lobbyStep.hidden = true;
  roleStep.hidden = false;
  phase.textContent = "Roles assigned";
  document.querySelector("#saboteur-name").textContent = players[0];
});

document.querySelector("#reveal-role").addEventListener("click", (event) => {
  event.currentTarget.hidden = true;
  document.querySelector("#role-instruction").hidden = true;
  document.querySelector("#revealed-role").hidden = false;
});

document.querySelector("#begin-task").addEventListener("click", () => {
  roleStep.hidden = true;
  taskStep.hidden = false;
  phase.textContent = "Task round";
});

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    sabotages = button.dataset.action === "sabotage" ? 1 : 0;
    document.querySelector("#sabotage-count").textContent = String(sabotages);
    taskStep.hidden = true;
    voteStep.hidden = false;
    phase.textContent = "Voting";
  });
});

voteStep.addEventListener("submit", (event) => {
  event.preventDefault();
  const target = Number(new FormData(voteStep).get("vote"));
  const caught = target === 0;
  document.querySelector("#result-title").textContent = caught
    ? "Saboteur identified."
    : "The saboteur survives.";
  document.querySelector("#result-copy").textContent = caught
    ? `Your vote identified ${players[0]}, so the sabotage points are removed.`
    : `Your vote missed ${players[0]}, so the sabotage points remain.`;
  document.querySelector("#point-count").textContent = String(caught ? 0 : sabotages);
  voteStep.hidden = true;
  resultStep.hidden = false;
  phase.textContent = "Round complete";
});

document.querySelector("#reset").addEventListener("click", () => window.location.reload());
