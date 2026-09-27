"use strict";

const taskStep = document.querySelector("#task-step");
const voteStep = document.querySelector("#vote-step");
const resultStep = document.querySelector("#result-step");
const phase = document.querySelector("#phase");
const mayaState = document.querySelector("#maya-state");
const sabotageCount = document.querySelector("#sabotage-count");
const pointCount = document.querySelector("#point-count");
let sabotages = 0;

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    sabotages = button.dataset.action === "sabotage" ? 1 : 0;
    sabotageCount.textContent = String(sabotages);
    taskStep.hidden = true;
    voteStep.hidden = false;
    phase.textContent = "Voting";
    mayaState.textContent = sabotages ? "Task sabotaged" : "Task completed";
  });
});

voteStep.addEventListener("submit", (event) => {
  event.preventDefault();
  const target = new FormData(voteStep).get("vote");
  const caught = target === "maya";
  document.querySelector("#result-title").textContent = caught ? "Innocents win." : "The saboteur survives.";
  document.querySelector("#result-copy").textContent = caught
    ? "The vote identified Maya, so her sabotage points are removed."
    : "The vote missed Maya, so she keeps the points from this round.";
  pointCount.textContent = String(caught ? 0 : sabotages);
  voteStep.hidden = true;
  resultStep.hidden = false;
  phase.textContent = "Round complete";
});

document.querySelector("#reset").addEventListener("click", () => window.location.reload());
