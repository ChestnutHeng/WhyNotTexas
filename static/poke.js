//import Phaser from "phaser";
import { TextButton } from './plugin/text_button.js';
import { Button } from './plugin/altas_button.js';
//import io from 'socket.io-client';
//import UIPlugin from './assets/rexuiplugin.min.js';

var config = {
    type: Phaser.AUTO,
    width: 1280,
    height: 720,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
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
    },
    plugins: {
        // scene: [{
        //     key: 'rexUI',
        //     plugin: UIPlugin,
        //     mapping: 'rexUI'
        // }
        // ]
    }
};

var game = new Phaser.Game(config);

function preload ()
{
    //this.load.image('sky', 'assets/sky.png');
    //this.load.spritesheet('dude', 'assets/dude.png', { frameWidth: 32, frameHeight: 48 });
    let rootDir = '../static/assets/'
    this.load.image('sky', rootDir + 'sky.png');
    this.load.pack('pokes', rootDir + 'asset.json', null, this);

    this.load.spritesheet('button', rootDir + 'button_sprite_sheet.png', { frameWidth: 193, frameHeight: 71 })
    this.load.atlas('buttonAtlas', rootDir+'button_texture_atlas.png', rootDir+'button_texture_atlas.json')

    this.load.scenePlugin({
        key: 'rexuiplugin',
        url: rootDir + 'rexuiplugin.min.js',
        sceneKey: 'rexUI'
    });

    console.log("loaded");
}

function create ()
{
    //game.scale.scaleMode = Phaser.ScaleManager.EXACT_FIT;
    //this.add.image(0, 0, '2C');
    //this.add.image(400, 300, 'sky');

    this.rivers = [];
    var cardScale = 0.2;
    var cardWidth = 691;
    var cardHeight = 1056;
    var cardActWidth = cardWidth * cardScale;
    var spanWidth = (this.game.config.width - cardActWidth*5)/6;
    const COLOR_PRIMARY = 0x4e342e;
    for(var i = 0; i < 5; ++i){
        var card = this.physics.add.sprite(cardActWidth*(i+0.5)+ spanWidth*(i+1), this.game.config.height/9*3, 'red_back');
        //console.log(this);
        card.setScale(cardScale, cardScale);
        this.rivers.push(card);
    }
    this.isSetRiverCount = 0
    
    this.card = this.physics.add.sprite(this.game.config.width/3, this.game.config.height/9*7, 'red_back');
    this.card.setScale(cardScale, cardScale);
    this.card2 = this.physics.add.sprite(this.game.config.width/3 + cardActWidth*0.2, this.game.config.height/9*7, 'red_back');
    this.card2.setScale(cardScale, cardScale); 
    this.isSetHand = false;     

    this.textArea = this.rexUI.add.textArea({
            x: this.game.config.width/8,
            y: this.game.config.height/9*7,
            width: 240,
            height: 240,
            background: this.rexUI.add.roundRectangle(0, 0, 2, 2, 0, COLOR_PRIMARY),
            slider: {
                track: this.rexUI.add.roundRectangle(0, 0, 20, 10, 10, 0x260e04),
                thumb: this.rexUI.add.roundRectangle(0, 0, 0, 0, 13, 0x7b5e57),
            },
            scroller: true,
        })
        .layout()
        .drawBounds(this.add.graphics(), 0xff0000);
    this.textArea.setText(this.textArea.text + CreateContent(1));
    /*
    this.clickButton = new TextButton(this, 100, 100, 'Check', { fill: '#0f0'}, () => CheckButtonClickHandler());
    this.add.existing(this.clickButton);
    */
    //let msgBox = this.physics.add.Text(this.game.config.width/8, this.game.config.height/9*6, { fill: '#ff0'});

    let btnCheck = new Button(this, this.game.config.width/2, this.game.config.height/9*6,
         'button', CheckButtonClickHandler, 2, 1, 0);
    btnCheck.setOrigin(0)

    let btnFold = new Button(this, this.game.config.width/2, this.game.config.height/9*7.5,
         'button', FoldButtonClickHandler, 2, 1, 0);
    btnFold.setOrigin(0)

    let btnAdd = new Button(this, this.game.config.width/4*3, this.game.config.height/9*6,
         'button', AddButtonClickHandler, 2, 1, 0);
    btnAdd.setOrigin(0)

    let btnPrepare = new Button(this, this.game.config.width/4*3, this.game.config.height/9*7.5,
         'button', PrepareButtonClickHandler, 2, 1, 0);
    btnPrepare.setOrigin(0)

    // this.socket = io('ws://localhost:4640/tex/ws');
    
    // this.socket.on('connect', function () {
    //     console.log('Connected!');
    // });

    // for flask csrf
    let father = this;
    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        },
        url: '/tex/api',
        type: 'POST',
        //dataType: 'json',
        contentType: 'application/json',
        error: function(res){
            console.log('ajax post error:', res)
        },
        success: function(res){
            RespHandler(res, father)
        }
    })
    console.log(csrftoken)

    // closure

    // timer
    setInterval(function () {
        $.ajax({
            data: JSON.stringify({"func":'tick'}),
        })
    },5000)
    $.ajax({
        data: JSON.stringify({"func":'tick'}),
    })
}

function update ()
{
    
}

function CheckButtonClickHandler(father) {
    console.log('click check')
    // ws = new WebSocket("ws://localhost:4640/tex/ws"); 
    // ws.send("HAHA")         
    // ws.onmessage = function (msg) {                                  
    //     console.log("<p>"+msg.data+"</p>")                      
    // };
    // var xhr = new XMLHttpRequest();
    // xhr.open('POST','://localhost:4640/tex/ws');
    // xhr.onreadystatechange = function(){
    //       ajax();
    // };
    // xhr.send();
    
    // self.socket.emit('cardPlayed', gameObject, self.isPlayerA);
    $.ajax({
        data: JSON.stringify({"func":'check'}),
    });
}

function RespHandler(res, father){
    console.log('father', father);
    console.log('RespHandler succ:', res);
    if (res['textbox']){
        father.textArea.setText(father.textArea.text + res['textbox'].join('\n'));
    };
    if (res['msgQ']){
        for(var i = 0; i < res['msgQ'].length; i++){
            let hook = res['msgQ'][i]['func_hook']
            if (hook) {
                handleHook(hook);
            }

        };
    };
    if (res['hook_func']){
        for(var i = 0; i < res['hook_func'].length; i++){
            handleHook(res['hook_func'][i])
        }
    }
    if (res['user_hand'] && res['user_hand'].length == 2 && !father.isSetHand){
        showUserHands(res['user_hand']);
        father.isSetHand = true;
    }

    if (res['river'] && father.rivers.length > father.isSetRiverCount){
        openCards(res['river']);
        father.isSetRiverCount = res['river'].length;
    }

    function handleHook(hook){
        switch(hook){
            // case 'showUserHands':
            //     showUserHands(res['user_hand'])
            case 'openCards':
                openCards(res['river'])
                father.isSetRiverCount = res['river'].length;
            case 'endGame':
                endGame(res['msgQ'])
            case 'startGame':
                startGame()
            default:
                
        };
    }

    function showUserHands(hand) {
        father.card.setTexture(hand[0]);
        father.card2.setTexture(hand[1]);
    };

    function openCards(river) {
        for(var i = 0; i < river.length; i++){
            father.rivers[i].setTexture(river[i]);
        }
    };

    function endGame(msg) {
        
    };
    function startGame() {
        for(var i = 0; i < father.rivers.length; i++){
            father.rivers[i].setTexture('red_back');
        }
        father.isSetHand = false;
        father.isSetRiverCount = 0;
    };
}

function FoldButtonClickHandler(father) {
    console.log('click fold')
    $.ajax({
        data: JSON.stringify({"func":'fold'}),
    });
}

function AddButtonClickHandler(father) {
    console.log('click add');
    $.ajax({
        data: JSON.stringify({"func":'add', 'add_money':'1'}),
    });
}

function PrepareButtonClickHandler(father){
    console.log('click prepare');
    $.ajax({
        data: JSON.stringify({"func":'prepare'}),
    });
}

function CreateContent (linesCount) {
    // var numbers = [];
    // for (var i = 0; i < linesCount; i++) {        
    //     numbers.push('[color=' + ((i % 2) ? 'green' : 'yellow') + ']' + i.toString() + '[/color]');
    // }
    // return 'bbbb \n' + numbers.join('\n');
    return '已加入房间\n'
}

/*
window.onload = function () {
    window.focus();
    resize();
    window.addEventListener('resize', resize, false);
}

function resize() {
    var canvas = document.querySfatherctor('canvas');
    var windowWidth = window.innerWidth;
    var windowHeight = window.innerHeight;
    var windowRatio = windowWidth / windowHeight;
    var gameRatio =  game.config.width / game.config.height;
    if (windowRatio < gameRatio) {
        canvas.style.width = windowWidth + 'px';
        canvas.style.height = (windowWidth / gameRatio) + 'px';
    } else {
        canvas.style.width = (windowHeight * gameRatio) + 'px';
        canvas.style.height = windowHeight + 'px';
    }
}
*/