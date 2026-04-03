const PRELOADED_CANDIES = [
    { name: "Sour Candy", count: 2, img: "assets/sour candy.png" },
    { name: "Lollipop", count: 3, img: "assets/lollipop.png" },
    { name: "Milk Chocolate", count: 5, img: "assets/chocolate.png" },
    { name: "Toffee", count: 6, img: "assets/toffee.png" }
];

let CANDY_TYPES = {};
let root;
let allNodes = [];

// DOM Elements Mappings
const screens = {
    title: document.getElementById('title-screen'),
    cutscene: document.getElementById('cutscene-screen'),
    story: document.getElementById('story-screen'),
    game: document.getElementById('game-screen'),
    end: document.getElementById('end-screen')
};

const linesSvg = document.getElementById('lines-svg');
const svgNS = "http://www.w3.org/2000/svg";

function showScreen(name) {
    Object.values(screens).forEach(s => s.classList.remove('active-screen'));
    screens[name].classList.add('active-screen');
}

// Button Events
document.getElementById('start-btn').onclick = () => {
    showScreen('cutscene');
    const video = document.getElementById('cutscene-video');
    video.currentTime = 0;
    video.play().catch(e => console.log('Video auto-play blocked, wait for user interaction:', e));
};

document.getElementById('cutscene-video').onended = () => showScreen('story');
document.getElementById('skip-cutscene-btn').onclick = () => {
    document.getElementById('cutscene-video').pause();
    showScreen('story');
};
document.getElementById('replay-cutscene-btn').onclick = () => {
    showScreen('cutscene');
    const video = document.getElementById('cutscene-video');
    video.currentTime = 0;
    video.play().catch(e => console.log('Video auto-play blocked', e));
};

let isMuted = false;
document.getElementById('mute-btn').onclick = () => {
    isMuted = !isMuted;
    document.getElementById('game-bgm').muted = isMuted;
    document.getElementById('mute-btn').innerHTML = isMuted ? '🔇' : '🔊';
};

document.getElementById('restart-lvl-btn').onclick = () => {
    setupNewGame();
    // Ensure music is continuously playing when restarting
    const bgm = document.getElementById('game-bgm');
    if(bgm.paused) bgm.play().catch(e => console.log(e));
};

document.getElementById('story-btn').onclick = () => {
    showScreen('game');
    const bgm = document.getElementById('game-bgm');
    bgm.volume = 0.5; // Set a reasonable default volume
    bgm.play().catch(e => console.log('Audio auto-play blocked:', e));
    setupNewGame();
};

document.getElementById('replay-btn').onclick = () => {
    const bgm = document.getElementById('game-bgm');
    bgm.pause();
    bgm.currentTime = 0;
    showScreen('title');
};

// -------------------------------------------------------------
// Interactive Node Visualizer Object
// -------------------------------------------------------------
class Node {
    constructor(candies, level, indexInLevel) {
        this.candies = [...candies];
        this.maxSize = candies.length;
        this.level = level;
        this.indexInLevel = indexInLevel;
        
        this.left = null;
        this.right = null;
        this.parent = null;
        
        this.state = this.maxSize === 1 ? "MERGED" : "IDLE";
        this.currentVisualCandies = []; 
        
        this.createDOM();
    }
    
    createDOM() {
        this.dom = document.createElement('div');
        this.dom.className = 'node ' + this.state.toLowerCase();
        
        let screenWidth = window.innerWidth;
        let screenHeight = window.innerHeight;
        
        // Horizontal constraint mapping to stay perfectly to the right of the Legends module
        let treeStartX = Math.max(screenWidth * 0.23, 280);
        let treeWidth = screenWidth - treeStartX - 20;
        let sectionWidth = treeWidth / (1 << this.level);
        
        this.x = treeStartX + (this.indexInLevel + 0.5) * sectionWidth;
        this.y = screenHeight * 0.20 + this.level * ((screenHeight * 0.65) / 4.0);
        
        this.dom.style.left = this.x + 'px';
        this.dom.style.top = this.y + 'px';
        
        // Draw native structural indexing placeholders
        for(let i=0; i<this.maxSize; i++) {
            let slot = document.createElement('div');
            slot.className = 'slot';
            slot.innerHTML = `<div class="slot-idx">[${i}]</div>`;
            this.dom.appendChild(slot);
        }
        
        // Draw distinct Pink Dashed Line showing where standard Merge Arrays partition mathematics execute
        if (this.state === "IDLE" && this.maxSize > 1) {
            let splitLine = document.createElement('div');
            splitLine.className = 'split-line';
            let mid = Math.floor(this.maxSize / 2);
            // Size mappings via CSS constraints calculation
            splitLine.style.left = (6 + mid * 52 - 2) + 'px'; // 6px padding + N * 52px (48px box + 4px flex-gap) - 2px center alignment
            this.dom.appendChild(splitLine);
            
            // Interaction to actually click and apply division step
            this.dom.onclick = () => this.divide();
        }
        
        document.getElementById('game-container').appendChild(this.dom);
    }
    
    updateDOMState() {
        this.dom.className = 'node ' + this.state.toLowerCase();
        if(this.state === "DIVIDED" && this.left.state === "MERGED" && this.right.state === "MERGED") {
            this.dom.classList.add("merge-ready");
        }
        
        // Smoothly hide layers that are entirely processed to eliminate visual bulk overheads
        if(this.parent && this.parent.state === "MERGED") {
            this.dom.style.opacity = '0';
            setTimeout(() => this.dom.style.display = 'none', 300);
        }
    }
    
    drawCandies() {
        for(let i=0; i<this.candies.length; i++) {
            let val = this.candies[i];
            let candy = document.createElement('img');
            candy.src = CANDY_TYPES[val].img;
            candy.className = 'candy-item non-interactive';
            
            candy.candyValue = val;
            candy.currentNode = this;
            
            candy.onclick = (e) => handleCandyClick(e, candy);
            
            let slot = this.dom.querySelectorAll('.slot')[i];
            slot.appendChild(candy);
            this.currentVisualCandies.push(candy);
        }
    }
    
    divide() {
        if(this.state !== "IDLE") return;
        
        let mid = Math.floor(this.maxSize / 2);
        
        // Creates Child logic dependencies
        this.left = new Node(this.candies.slice(0, mid), this.level + 1, this.indexInLevel * 2);
        this.right = new Node(this.candies.slice(mid), this.level + 1, this.indexInLevel * 2 + 1);
        
        this.left.parent = this;
        this.right.parent = this;
        allNodes.push(this.left, this.right);
        
        this.state = "DIVIDED";
        this.candies = [];
        this.dom.onclick = null;
        
        this.currentVisualCandies.forEach(c => c.remove());
        this.currentVisualCandies = [];
        
        this.left.drawCandies();
        this.right.drawCandies();
        
        drawLines();
        updateAllNodes();
        checkPhase();
        
        setMessage("Divided the array into two smaller halves!", "#5096ff");
    }
}

// Global UI Rendering Helpers
function updateAllNodes() {
    allNodes.forEach(n => n.updateDOMState());
    drawLines();
}

function drawLines() {
    linesSvg.innerHTML = '';
    allNodes.forEach(child => {
        if(child.parent && child.parent.state !== "MERGED") {
            let px = child.parent.x;
            let py = child.parent.y + child.parent.dom.offsetHeight/2;
            let cx = child.x;
            let cy = child.y - child.dom.offsetHeight/2;
            
            // White Outer Core
            let lineOuter = document.createElementNS(svgNS, 'line');
            lineOuter.setAttribute('x1', px); lineOuter.setAttribute('y1', py);
            lineOuter.setAttribute('x2', cx); lineOuter.setAttribute('y2', cy);
            lineOuter.setAttribute('stroke', 'white'); lineOuter.setAttribute('stroke-width', '7');
            linesSvg.appendChild(lineOuter);
            
            // Purple Inner Core
            let lineInner = document.createElementNS(svgNS, 'line');
            lineInner.setAttribute('x1', px); lineInner.setAttribute('y1', py);
            lineInner.setAttribute('x2', cx); lineInner.setAttribute('y2', cy);
            lineInner.setAttribute('stroke', '#b464ff'); lineInner.setAttribute('stroke-width', '3');
            linesSvg.appendChild(lineInner);
        }
    });
}

function checkPhase() {
    let allDivided = !allNodes.some(n => n.state === "IDLE");
    if(allDivided && !root.mergePhaseStarted) {
        root.mergePhaseStarted = true;
        
        // Set leaf nodes to click-state directly
        allNodes.forEach(n => {
            n.currentVisualCandies.forEach(c => c.classList.remove('non-interactive'));
        });
        
        setMessage("MERGE PHASE: Everything is divided. Click the smaller candy to merge!", "#3cdc64");
    }
}


function setMessage(msg, color) {
    let topMsg = document.getElementById('top-message');
    topMsg.innerHTML = msg;
    topMsg.style.color = color;
    topMsg.style.borderColor = color;
}

// Interactive Handling Physics Controller 
function handleCandyClick(e, candyDOM) {
    let node = candyDOM.currentNode;
    let parent = node.parent;
    if(!parent) return;
    
    // Bounds Check constraints
    if(parent.state !== "DIVIDED" || parent.left.state !== "MERGED" || parent.right.state !== "MERGED") return;
    
    let isLeft = (node === parent.left);
    let sibling = isLeft ? parent.right : parent.left;
    
    // Evaluate Merge Sort index 0 bounds checking natively
    if(candyDOM !== node.currentVisualCandies[0]) return;
    
    let siblingVal = (sibling && sibling.currentVisualCandies.length > 0) ? sibling.currentVisualCandies[0].candyValue : Infinity;
    let myVal = candyDOM.candyValue;
    
    let isValid = (myVal <= siblingVal);
    
    if(isValid) {
        // Shift logical array memory pointers
        node.currentVisualCandies.shift(); 
        parent.currentVisualCandies.push(candyDOM); 
        candyDOM.currentNode = parent;
        
        // Utilize FLIP animations moving it locally between respective Slot nodes
        let targetSlotIdx = parent.currentVisualCandies.length - 1;
        let targetSlotDOM = parent.dom.querySelectorAll('.slot')[targetSlotIdx];
        
        let first = candyDOM.getBoundingClientRect();
        targetSlotDOM.appendChild(candyDOM);
        let last = candyDOM.getBoundingClientRect();
        
        let deltaX = first.left - last.left;
        let deltaY = first.top - last.top;
        let scaleX = first.width / last.width;
        let scaleY = first.height / last.height;
        
        candyDOM.animate([
            { transform: `translate(${deltaX}px, ${deltaY}px) scale(${scaleX}, ${scaleY})` },
            { transform: `translate(0, 0) scale(1, 1)` }
        ], { duration: 400, easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)' });
        
        if(siblingVal !== Infinity) {
            setMessage(`Correct! ${CANDY_TYPES[myVal].name} (${myVal}) is <= ${CANDY_TYPES[siblingVal].name} (${siblingVal}).`, "#3cdc64");
        } else {
            setMessage(`Correct! Other tray empty.`, "#3cdc64");
        }
        
        // Evaluate completion checks upstream!
        if(parent.currentVisualCandies.length === parent.maxSize) {
            parent.state = "MERGED";
            if(parent !== root) {
                parent.currentVisualCandies.forEach(c => c.classList.remove('non-interactive'));
            } else {
                setMessage("Perfectly Sorted! Fashion Show Time!", "#3cdc64");
                
                let videoFrame = document.getElementById('video-frame');
                let videoObj = document.getElementById('guide-video');
                
                // Trigger the massive fullscreen zoom effect
                videoFrame.classList.add('zoomed');
                videoObj.style.objectFit = 'cover'; // Fit perfectly to scale!
                
                setTimeout(() => {
                    // Update to the final hooray victory video!
                    videoObj.src = "assets/animate (4).mp4";
                    videoObj.muted = false;
                    videoObj.loop = false;
                    
                    // Synthesize an adorable "Hooray"!
                    let hooray = new SpeechSynthesisUtterance("Hooray! The fashion show was a huge success!");
                    hooray.pitch = 1.5; // Elevate pitch for a brighter tone
                    hooray.rate = 1.1;
                    
                    // Attempt to locate a distinct female voice from OS/Browser
                    let voices = window.speechSynthesis.getVoices();
                    let girlVoice = voices.find(v => /zira|samantha|victoria|karen|tessa|moira|fiona|female|google uk english female/i.test(v.name));
                    if (!girlVoice) girlVoice = voices.find(v => /google us english/i.test(v.name)); // Chrome fallback
                    
                    if (girlVoice) hooray.voice = girlVoice;
                    
                    window.speechSynthesis.speak(hooray);
                    
                    videoObj.play().catch(e => console.log('Hooray video block:', e));
                    
                    videoObj.onended = () => {
                        // Freeze frame prompt!
                        let overlay = document.getElementById('video-freeze-overlay');
                        overlay.style.display = 'flex';
                        
                        overlay.onclick = () => {
                            overlay.style.display = 'none';
                            showScreen('end');
                            videoFrame.classList.remove('zoomed');
                            
                            // Restate the looped guide video for the next round
                            videoObj.src = "assets/animate (2).mp4";
                            videoObj.muted = true;
                            videoObj.loop = true;
                            videoObj.play();
                        };
                    };
                }, 1200); // 1.2s delay to wait for the CSS transform to finish snapping!
            }
            updateAllNodes();
        }
        
        // Natively shifts all remaining local items dynamically forward automatically 
        node.currentVisualCandies.forEach((c, idx) => {
            let sDOM = node.dom.querySelectorAll('.slot')[idx];
            let cFirst = c.getBoundingClientRect();
            sDOM.appendChild(c);
            let cLast = c.getBoundingClientRect();
            let dX = cFirst.left - cLast.left;
            let dY = cFirst.top - cLast.top;
            if(dX !== 0 || dY !== 0) {
                c.animate([
                    { transform: `translate(${dX}px, ${dY}px)` },
                    { transform: `translate(0, 0)` }
                ], { duration: 400, easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)' });
            }
        });
        
    } else {
        node.dom.classList.add('error');
        setTimeout(() => node.dom.classList.remove('error'), 400); // clear CSS keyframe error animation
        setMessage(`Oops! ${CANDY_TYPES[myVal].name} > ${CANDY_TYPES[siblingVal].name}. Pick smaller!`, "#ff3278");
    }
}

// Start Runtime Initializations
function setupNewGame() {
    document.getElementById('game-container').innerHTML = '';
    document.getElementById('candies-container').innerHTML = '';
    linesSvg.innerHTML = '';
    
    let bases = [...PRELOADED_CANDIES].sort(() => Math.random() - 0.5);
    let initialBag = [];
    CANDY_TYPES = {};
    
    let legendHtml = `<h2>Runway Order</h2>`;
    
    bases.forEach((base, i) => {
        let val = i + 1;
        CANDY_TYPES[val] = { name: base.name, img: base.img };
        legendHtml += `<div class="legend-item"><img src="${base.img}"> ${val}. ${base.name}</div>`;
        for(let c=0; c<base.count; c++) initialBag.push(val);
    });
    
    document.getElementById('legend').innerHTML = legendHtml;
    
    initialBag.sort(() => Math.random() - 0.5); // Arrays securely randomized
    
    allNodes = [];
    root = new Node(initialBag, 0, 0);
    allNodes.push(root);
    root.drawCandies();
    
    root.mergePhaseStarted = false;
    setMessage("DIVIDE PHASE: Click on the pink outlined boxes to divide the arrays!", "#ff69b4");
}
