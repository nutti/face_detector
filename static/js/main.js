"use strict";
class Main {
	constructor(canvas, message, json) {
		this.width = canvas.width;
		this.height = canvas.height;
		this.ctx = canvas.getContext('2d');
		this.message = $(message);
		this.json = $(json);
	}
	load(url) {
		const img = new Image();
		img.onload = () => {
			const scale = Math.max(img.width / this.width, img.height / this.height);
			const w = img.width / scale;
			const h = img.height / scale;
			const offset_x = (this.width - w) / 2.0;
			const offset_y = (this.height - h) / 2.0;
			this.fillStyle = 'rgb(0, 0, 0)';
			this.ctx.fillRect(0, 0, this.width, this.height);
			this.ctx.drawImage(img, offset_x, offset_y, w, h);
			$.ajax({
				url: 'api',
				data: {
					url: url
				},
				success: (result) => {
					this.message.text('face detected');
					this.json.text(JSON.stringify(result), null, '    ');
					var region = result.region;
					var tx = region.x / scale;
					var ty = region.y / scale;
					var tw = region.width / scale;
					var th = region.height / scale
					this.ctx.beginPath();
					this.ctx.moveTo(tx, ty);
					this.ctx.lineTo(tx + tw, ty);
					this.ctx.lineTo(tx + tw, ty + th);
					this.ctx.lineTo(tx, ty + th);
					this.ctx.closePath();
					this.ctx.lineWidth = 2;
					this.ctx.strokeStyle = 'rgb(0, 255, 0)';
					this.ctx.stroke();
				}
			});
		};
		img.onerror = () => {
			this.message.text('error!!');
		}
		img.src = this.url = url;
	}
}

$(() => {
	const main = new Main(
		document.getElementById('canvas'),
		document.getElementById('message'),
		document.getElementById('json')
	);
	$('#url').submit(() => {
		const url = $('input[name="image_url"]').val();
		if (url) {
			main.load(url);
		}
		return false;
	});
			
});

