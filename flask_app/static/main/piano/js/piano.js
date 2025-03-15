document.addEventListener("DOMContentLoaded", () => {
    console.log("Piano script loaded!"); // Debugging Check

    const sound = {
        65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
        87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
        83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
        69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
        68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
        70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
        84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
        71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
        89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
        72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
        85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
        74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
        75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
        79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
        76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
        80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
        186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"
    };

    // Play sound when a key is pressed
    document.addEventListener("keydown", function(event) {
        console.log(`Key pressed: ${event.keyCode}`); // Debugging
        let key = document.querySelector(`.piano div[data-key="${event.keyCode}"]`);
        
        if (key && sound[event.keyCode]) {
            let audio = new Audio(sound[event.keyCode]);
            audio.play();

            // Apply visual effect
            key.classList.add("pressed");
            setTimeout(() => key.classList.remove("pressed"), 200);
        }
    });

    // Show letter on hover
    document.querySelectorAll(".piano div").forEach(key => {
        key.addEventListener("mouseenter", () => key.querySelector("span").style.display = "block");
        key.addEventListener("mouseleave", () => key.querySelector("span").style.display = "none");
    });

    console.log("Key listeners added!"); // Debugging Check
});
