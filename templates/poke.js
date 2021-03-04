//import Phaser from "phaser";

var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: 1280,
        height: 720,
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

function preload ()
{
    //this.load.image('sky', 'assets/sky.png');
    //this.load.spritesheet('dude', 'assets/dude.png', { frameWidth: 32, frameHeight: 48 });
    this.load.image('sky', 'assets/sky.png');
    this.load.pack('section', './asset.json');
}

function create ()
{
    this.add.image(400, 300, '2A');
    this.add.image(400, 300, 'sky');
}

function update ()
{


}