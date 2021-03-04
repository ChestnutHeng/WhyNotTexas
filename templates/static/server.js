var http = require('http');
var fs = require('fs')

var server = http.createServer( (req, res) => {
    fs.readFile('./part10.html',(err,data) =>{
        res.statusCode = 200;
        res.setHeader('Content-Type', 'text/html');
        if (!err) {
            res.end(data);
        }else {
            res.end('html not found');
        }
    });
})

server.listen(3000, () => {
    console.log('服务启动成功，监听3000端口')
})