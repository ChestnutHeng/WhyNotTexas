export class Button extends Phaser.GameObjects.Sprite {
    onInputOver = () => {}
    onInputOut = () => {}
    onInputUp = () => {}
  
    constructor(scene, x, y, texture, actionOnClick = (father) => {}, overFrame, outFrame, downFrame) {
      super(scene, x, y, texture)
      scene.add.existing(this)
  
      this.setFrame(outFrame)
        .setInteractive()
  
        .on('pointerover', () => {
          this.onInputOver()
          this.setFrame(overFrame)
        })
        .on('pointerdown', (father) => {
          actionOnClick(father)
          this.setFrame(downFrame)
        })
        .on('pointerup', () => {
          this.onInputUp()
          this.setFrame(overFrame)
        })
        .on('pointerout', () => {
          this.onInputOut()
          this.setFrame(outFrame)
        })
    }
  }

  /*
this.load.spritesheet('button', 'assets/button_sprite_sheet.png', { frameWidth: 193, frameHeight: 71 })
this.load.atlas('buttonAtlas', 'assets/button_texture_atlas.png', 'assets/button_texture_atlas.json')

const actionOnClick = () => {
  console.log('click')
}

let btn1 = new Button(this, 50, 50, 'button', actionOnClick, 2, 1, 0)
btn1.onInputOut = () => {
  console.log('Btn1: onInputOut')
}
btn1.setOrigin(0)

let btn2 = new Button(this, 50, 150, 'buttonAtlas', actionOnClick, 'over', 'out', 'down')
btn2.onInputOut = () => {
  console.log('Btn2: onInputOut')
}
btn2.setOrigin(0)
*/

