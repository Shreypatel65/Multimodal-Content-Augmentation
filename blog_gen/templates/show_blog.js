
function createAudio() {
    // Show loading overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "{{id}}/audio", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            // Hide loading overlay when the request is complete
            document.getElementById('loadingOverlay').style.display = 'none';
            window.location.reload();
        }
    };

    xhr.send();
}

    const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min
        const COUNT = 360 / 6
        const BTN = document.querySelectorAll('.button')
        const setParticles = (b) => {
            const PARTICLES = b.querySelectorAll('.heart__particle')
            PARTICLES.forEach((particle, index) => {
                const CHARACTER = {
                    '--d': random(30, 60),
                    '--r': (360 / 25) * index,
                    '--h': random(0, 360),
                    '--t': random(25, 50) / 100,
                    '--s': random(20, 60) / 100
                }
                particle.setAttribute(
                    'style',
                    JSON.stringify(CHARACTER)
                        .replace(/,/g, ';')
                        .substring(1, JSON.stringify(CHARACTER).length - 1)
                        .replace(/"/g, '')
                )
            })
        }
        BTN.forEach((b) => {
            setParticles(b)
            b.addEventListener('click', () => {
                b.classList.toggle('button--active')
                if (b.classList.contains('button--active')){
                    setParticles(b)
                    like()
                } else {
                    like()
                }
            })
        })
        function like() {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", "{{id}}/like", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send();
        }

        class musicPlayer {
            constructor() {
                this.play = this.play.bind(this);
                this.controlPanel = document.getElementById('control-panel');
                this.infoBar = document.getElementById('info');

                this.audio = new Audio("{{ source }}{{ blog.audio }}");
                
                this.playBtn = document.getElementById('play');
                this.playBtn.addEventListener('click', this.play);
        
                // Add event listener for 'ended' event
                this.audio.addEventListener('ended', this.handleAudioEnded.bind(this));
            }
        
            play() {
                let controlPanelObj = this.controlPanel;
                Array.from(controlPanelObj.classList).find(function (element) {
                    return element !== "active" ? controlPanelObj.classList.add('active') : controlPanelObj.classList.remove('active');
                });
        
                // Toggle play/pause
                if (this.audio.paused) {
                    this.audio.play();
                } else {
                    this.audio.pause();
                }
            }
        
            handleAudioEnded() {
                let controlPanelObj = this.controlPanel;
                controlPanelObj.classList.remove('active');
            }
        }
        
        const newMusicplayer = new musicPlayer();
        