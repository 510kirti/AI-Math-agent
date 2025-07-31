document.getElementById("solve").addEventListener("click", async () => {
  const expr = document.getElementById("expression").value;
  if (!expr.trim()) {
    alert("Please enter a math expression.");
    return;
  }

  // Reset outputs
  document.getElementById("perception-output").textContent = "🔍 Analyzing...";
  document.getElementById("memory-output").textContent = "🧠 Consulting memory...";
  document.getElementById("decision-output").textContent = "⚡ Deciding strategy...";
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
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ expression: expr })
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
  ? ""  // Hide result if it's an equation
  : `🧾 Result: ${data.action.result}\n`;

    document.getElementById("action-output").textContent = `
    ${resultText}
🔬 Verification: ${data.action.verification}
📝 Execution Notes: ${data.action.execution_notes}
🚀 Steps: \n${data.action.steps.join("\n")}
    `.trim();

    // ✅ Graph Plotting
    const graphMatch = expr.match(/^y\s*=\s*(.+)$/i);  // Match expressions like y = x^2
    if (graphMatch && graphCanvas) {
      const equation = graphMatch[1];
      console.log("✅ Attempting to graph:", equation); 
      const ctx = graphCanvas.getContext("2d");

      try {
        const parsedFunc = new Function("x", `return ${equation.replace(/\^/g, "**")};`);
        const width = graphCanvas.width;
        const height = graphCanvas.height;
        const scale = 20;

        ctx.clearRect(0, 0, width, height);
        ctx.beginPath();
        ctx.strokeStyle = "#007bff";

        let started = false;
        for (let px = 0; px < width; px++) {
          const x = (px - width / 2) / scale;
          let y;
          try {
            y = parsedFunc(x);
          } catch {
            continue;
          }
          const py = height / 2 - y * scale;
          if(!started)
          {
            ctx.moveTo(px,py);
            started = true;
          }
          else ctx.lineTo(px, py);
        }
        ctx.stroke();

        // Draw axes
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.moveTo(width / 2, 0);
        ctx.lineTo(width / 2, height);
        ctx.strokeStyle = "#aaa";
        ctx.stroke();

        // ✅ Show graph card
        document.getElementById("chart-container").style.display = "block";
      } catch (graphErr) {
        console.error("❌ Graph draw failed:", graphErr);
        document.getElementById("chart-container").style.display = "none";
      }
    } else {
      document.getElementById("chart-container").style.display = "none";
    }

  } catch (err) {
    console.error("❌ Error:", err);
    document.getElementById("perception-output").innerText = "❌ Failed to analyze.";
    document.getElementById("memory-output").innerText = "❌ Cannot proceed due to invalid expression.";
    document.getElementById("decision-output").innerText = "❌ Cannot proceed due to invalid expression.";
    document.getElementById("action-output").innerText = "❌ Cannot proceed due to invalid expression.";
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
