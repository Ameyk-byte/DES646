// script.js

const canvas = document.getElementById('sphereCanvas');
const ctx = canvas.getContext('2d');

// Set canvas dimensions
canvas.width = 500;
canvas.height = 500;

// Sphere properties
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const baseRadius = 150;
let amplitude = 0;
let pulseScale = 1; // Controls pulsation
let pulseDirection = 1; // 1 for expanding, -1 for contracting

// Audio setup
let audioContext, analyser, dataArray, source, stream;

// Button to start listening
const micButton = document.getElementById('micButton');
micButton.addEventListener('click', async () => {
  if (!audioContext) {
    await startAudio();
  }
});

async function startAudio() {
  try {
    // Initialize audio context
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    dataArray = new Uint8Array(analyser.frequencyBinCount);

    // Get user media (microphone)
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    // Start animation loop
    animateSphere();
  } catch (err) {
    console.error('Error accessing microphone:', err);
  }
}

function animateSphere() {
  requestAnimationFrame(animateSphere);

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Get frequency data
  analyser.getByteFrequencyData(dataArray);

  // Calculate average amplitude
  const avgAmplitude = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;
  amplitude = avgAmplitude / 10; // Scale down for smoother effect

  // Update pulsation scale
  pulseScale += pulseDirection * 0.01;
  if (pulseScale > 1.2 || pulseScale < 0.8) {
    pulseDirection *= -1; // Reverse direction
  }

  // Draw the reactive sphere
  drawSiriSphere(centerX, centerY, baseRadius, amplitude, pulseScale);
}

function drawSiriSphere(x, y, r, amp, pulse) {
  ctx.beginPath();

  // Create a distorted circle with wave-like ripples
  for (let angle = 0; angle < Math.PI * 2; angle += 0.01) {
    const dynamicRadius = r * pulse + Math.sin(angle * 10 + amp) * 10;
    const posX = x + dynamicRadius * Math.cos(angle);
    const posY = y + dynamicRadius * Math.sin(angle);
    if (angle === 0) {
      ctx.moveTo(posX, posY);
    } else {
      ctx.lineTo(posX, posY);
    }
  }

  // Style the sphere
  const gradient = ctx.createRadialGradient(x, y, r * pulse * 0.5, x, y, r * pulse);
  gradient.addColorStop(0, 'rgba(0, 123, 255, 0.8)');
  gradient.addColorStop(1, 'rgba(0, 123, 255, 0)');
  ctx.strokeStyle = gradient;
  ctx.lineWidth = 2;
  ctx.fillStyle = 'rgba(0, 123, 255, 0.2)';
  ctx.fill();
  ctx.stroke();
}