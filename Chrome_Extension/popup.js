document.getElementById("solve").addEventListener("click", async () => {
  const expr = document.getElementById("expression").value;
  if (!expr.trim()) {
    alert("Please enter a math expression.");
    return;
  }

  // Reset outputs
  document.getElementById("perception-output").textContent = "🔍 Analyzing...";
  document.getElementById("memory-output").textContent =
    "🧠 Consulting memory...";
  document.getElementById("decision-output").textContent =
    "⚡ Deciding strategy...";
  document.getElementById("action-output").textContent = "🚀 Solving...";
  const graphCanvas = document.getElementById("expressionChart");
  if (graphCanvas) {
    const ctx = graphCanvas.getContext("2d");
    ctx.clearRect(0, 0, graphCanvas.width, graphCanvas.height);
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/full", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ expression: expr }),
    });

    if (!response.ok) throw new Error("Server error or invalid expression.");
    const data = await response.json();

    // Update Cognitive Phase Cards
    document.getElementById("perception-output").textContent = `
✅ Valid: ${data.perception.is_valid}
📊 Complexity: ${data.perception.complexity}
🎯 Difficulty: ${data.perception.estimated_difficulty}/10
📌 Notes: ${data.perception.perception_notes}
    `.trim();

    document.getElementById("memory-output").textContent = `
🎯 Strategy: ${data.memory.strategy_recommendation}
📈 Confidence Modifier: ${data.memory.confidence_modifier}
🧠 Similar Problems Found: ${data.memory.similar_problems_found}
📝 Memory Insights: ${data.memory.memory_insights}
    `.trim();

    document.getElementById("decision-output").textContent = `
🧠 Method Chosen: ${data.decision.selected_method}
🎯 Final Confidence: ${data.decision.final_confidence}
🛡️ Verification Level: ${data.decision.verification_level}
📌 Reasoning: ${data.decision.reasoning}
    `.trim();

    const resultText = expr.includes("=")
      ? "" // Hide result if it's an equation
      : `🧾 Result: ${data.action.result}\n`;

    document.getElementById("action-output").textContent = `
    ${resultText}
🔬 Verification: ${data.action.verification}
📝 Execution Notes: ${data.action.execution_notes}
🚀 Steps: \n${data.action.steps.join("\n")}
    `.trim();

    // ✅ Graph Plotting
    const graphCanvas = document.getElementById("expressionChart");
const chartContainer = document.getElementById("chart-container");
const plotMessage = document.getElementById("plot-message");

// Check if the backend sent plot points
if (data.action.plot_points && data.action.plot_points.length > 0) {
    const plotPoints = data.action.plot_points;
    console.log("✅ Plotting graph from backend data:", plotPoints);

    // Show the graph container and canvas, hide the message
    chartContainer.style.display = "block";
    graphCanvas.style.display = "block";
    plotMessage.style.display = "none";

    const ctx = graphCanvas.getContext("2d");
    const width = graphCanvas.width;
    const height = graphCanvas.height;
    const scale = 10;

    // ... (rest of your plotting logic remains the same) ...
    // Clear canvas, draw points, and draw axes as before.
    ctx.clearRect(0, 0, width, height);
    ctx.beginPath();
    ctx.strokeStyle = "#007bff";

    let started = false;
    for (const point of plotPoints) {
        const px = width / 2 + point.x * scale;
        const py = height / 2 - point.y * scale;

        if (isNaN(px) || isNaN(py) || px < 0 || px > width || py < 0 || py > height) {
            started = false;
            continue;
        }

        if (!started) {
            ctx.moveTo(px, py);
            started = true;
        } else {
            ctx.lineTo(px, py);
        }
    }
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.strokeStyle = "#aaa";
    ctx.stroke();

} else {
    // If no plot points, show the message and hide the canvas
    const expr = document.getElementById("expression").value;
    const graphMatch = expr.match(/^y\s*=\s*(.+)$/i);
    
    if (graphMatch) {
        // If it's a valid function but no points were generated
        plotMessage.textContent = "Graph plotting failed. No valid points generated.";
    } else {
        // If it's not a function at all
        plotMessage.textContent = "Graph is not applicable for this expression.";
    }

    chartContainer.style.display = "block";
    graphCanvas.style.display = "none";
    plotMessage.style.display = "block";
  }
  } catch (err) {
    console.error("❌ Error:", err);
    document.getElementById("perception-output").innerText =
      "❌ Failed to analyze.";
    document.getElementById("memory-output").innerText =
      "❌ Cannot proceed due to invalid expression.";
    document.getElementById("decision-output").innerText =
      "❌ Cannot proceed due to invalid expression.";
    document.getElementById("action-output").innerText =
      "❌ Cannot proceed due to invalid expression.";
    document.getElementById("chart-container").style.display = "none";
  }
});

// document.getElementById("solve").addEventListener("click", async () => {
//   const expr = document.getElementById("expression").value;
//   const graphCanvas = document.getElementById("expressionChart");
//   const chartContainer = document.getElementById("chart-container");

//   if (!expr.trim()) {
//     alert("Please enter a math expression.");
//     return;
//   }

//   // Reset all outputs
//   document.getElementById("perception-output").textContent = "🔍 Analyzing...";
//   document.getElementById("memory-output").textContent = "🧠 Consulting memory...";
//   document.getElementById("decision-output").textContent = "⚡ Deciding strategy...";
//   document.getElementById("action-output").textContent = "🚀 Solving...";
//   chartContainer.style.display = "none";

//   try {
//     const response = await fetch("http://127.0.0.1:8000/full", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json"
//       },
//       body: JSON.stringify({ expression: expr })
//     });

//     if (!response.ok) throw new Error("Server error or invalid expression.");

//     const data = await response.json();

//     // Update cognitive phase outputs
//     document.getElementById("perception-output").textContent = `
// ✅ Valid: ${data.perception.is_valid}
// 📊 Complexity: ${data.perception.complexity}
// 🎯 Difficulty: ${data.perception.estimated_difficulty}/10
// 📌 Notes: ${data.perception.perception_notes}
//     `.trim();

//     document.getElementById("memory-output").textContent = `
// 🎯 Strategy: ${data.memory.strategy_recommendation}
// 📈 Confidence Modifier: ${data.memory.confidence_modifier}
// 🧠 Similar Problems Found: ${data.memory.similar_problems_found}
// 📝 Memory Insights: ${data.memory.memory_insights}
//     `.trim();

//     document.getElementById("decision-output").textContent = `
// 🧠 Method Chosen: ${data.decision.selected_method}
// 🎯 Final Confidence: ${data.decision.final_confidence}
// 🛡️ Verification Level: ${data.decision.verification_level}
// 📌 Reasoning: ${data.decision.reasoning}
//     `.trim();

//     document.getElementById("action-output").textContent = `
// 🧾 Result: ${data.action.result}
// 🔬 Verification: ${data.action.verification}
// 📝 Execution Notes: ${data.action.execution_notes}
// 🚀 Steps: \n${data.action.steps.join("\n")}
//     `.trim();

//     // ✅ Graph Plotting
//     const graphMatch = expr.match(/^y\s*=\s*(.+)$/i); // flexible pattern
//     if (graphMatch && graphCanvas) {
//       const equation = graphMatch[1];
//       const ctx = graphCanvas.getContext("2d");

//       try {
//         const parsedFunc = new Function("x", `return ${equation.replace(/\^/g, "**")};`);
//         const width = graphCanvas.width;
//         const height = graphCanvas.height;
//         const scale = 20;

//         ctx.clearRect(0, 0, width, height);
//         ctx.beginPath();
//         ctx.strokeStyle = "#007bff";

//         for (let px = 0; px < width; px++) {
//           const x = (px - width / 2) / scale;
//           let y;
//           try {
//             y = parsedFunc(x);
//           } catch {
//             continue;
//           }
//           const py = height / 2 - y * scale;
//           if (px === 0) ctx.moveTo(px, py);
//           else ctx.lineTo(px, py);
//         }
//         ctx.stroke();

//         // Draw Axes
//         ctx.beginPath();
//         ctx.moveTo(0, height / 2);
//         ctx.lineTo(width, height / 2);
//         ctx.moveTo(width / 2, 0);
//         ctx.lineTo(width / 2, height);
//         ctx.strokeStyle = "#aaa";
//         ctx.stroke();

//         // ✅ Show graph card only after successful drawing
//         chartContainer.style.display = "block";
//       } catch (graphError) {
//         console.warn("⚠️ Failed to plot graph:", graphError);
//         chartContainer.style.display = "none";
//       }
//     } else {
//       chartContainer.style.display = "none";
//     }

//   } catch (err) {
//     console.error("❌ Error:", err);
//     document.getElementById("perception-output").innerText = "❌ Failed to analyze.";
//     document.getElementById("memory-output").innerText = "❌ Cannot proceed due to invalid expression.";
//     document.getElementById("decision-output").innerText = "❌ Cannot proceed due to invalid expression.";
//     document.getElementById("action-output").innerText = "❌ Cannot proceed due to invalid expression.";
//     chartContainer.style.display = "none";
//   }
// });

// document.getElementById("solve").addEventListener("click", async () => {
//   const expression = document.getElementById("expression").value.trim();
//   if (!expression) return;

//   // Reset outputs
//   document.getElementById("perception-output").textContent = "Processing...";
//   document.getElementById("memory-output").textContent = "Processing...";
//   document.getElementById("decision-output").textContent = "Processing...";
//   document.getElementById("action-output").textContent = "Processing...";

//   try {
//     const response = await fetch("http://localhost:8000/solve", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ expression }),
//     });

//     const data = await response.json();

//     document.getElementById("perception-output").textContent = data.perception;
//     document.getElementById("memory-output").textContent = data.memory;
//     document.getElementById("decision-output").textContent = data.decision;
//     document.getElementById("action-output").textContent = data.action;

//     // Attempt to plot the expression
//     plotExpression(expression);
//   } catch (error) {
//     console.error("Error:", error);
//     document.getElementById("action-output").textContent = "❌ Failed to solve.";
//   }
// });

// // Plotting logic using Chart.js
// let chartInstance = null;

// function plotExpression(expr) {
//   try {
//     const xValues = [];
//     const yValues = [];

//     for (let x = -10; x <= 10; x += 0.5) {
//       const y = evaluateExpression(expr, x);
//       if (typeof y === "number" && isFinite(y)) {
//         xValues.push(x);
//         yValues.push(y);
//       }
//     }

//     const ctx = document.getElementById("expressionChart").getContext("2d");

//     if (chartInstance) {
//       chartInstance.destroy(); // Clear previous chart
//     }

//     chartInstance = new Chart(ctx, {
//       type: "line",
//       data: {
//         labels: xValues,
//         datasets: [
//           {
//             label: `f(x) = ${expr}`,
//             data: yValues,
//             borderColor: "#28a745",
//             borderWidth: 2,
//             fill: false,
//             pointRadius: 0,
//             tension: 0.2,
//           },
//         ],
//       },
//       options: {
//         responsive: true,
//         plugins: {
//           legend: { display: false },
//         },
//         scales: {
//           x: { title: { display: true, text: "x" } },
//           y: { title: { display: true, text: "f(x)" } },
//         },
//       },
//     });
//   } catch (err) {
//     console.warn("Graph Error:", err.message);
//   }
// }

// // Safely evaluate expression at given x
// function evaluateExpression(expr, x) {
//   try {
//     const safeExpr = expr.replace(/[^0-9x+\-*/().^ ]/g, "").replace(/\^/g, "**");
//     return Function(`"use strict"; let x = ${x}; return ${safeExpr};`)();
//   } catch {
//     return NaN;
//   }
// }
