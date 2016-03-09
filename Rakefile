require 'open-uri'
require 'date'
require 'logger'
require 'nokogiri'
require 'json'

require 'net/http'
require 'uri'
require 'rmagick'


namespace :tf_app do
	proxy_file_path = 'proxy.json'
	data = open(proxy_file_path) do |io|
		JSON.load(io)
	end
	pxy = data['proxy']
	usr = data['user']
	pss = data['password']
	options = { :proxy_http_basic_authentication => [pxy,usr,pss] }

	task :api, %w(uri face_type) do |_task, args|
		uri = URI('http://localhost:5000/api')
		params = {:url => args.uri, :face_type => args.face_type}
		uri.query = URI.encode_www_form(params)
		res = Net::HTTP.get_response(uri)
		parsed = JSON.parse(res.body)
		image = Magick::ImageList.new
		urlimage = open(parsed['url'], options)
		image.from_blob(urlimage.read)
		processed_image = image.crop(parsed['region']['x'], parsed['region']['y'], parsed['region']['width'], parsed['region']['height'])
		resized_image = processed_image.resize(32, 32)
		resized_image.write('processed.jpg')
	end

	logger = Logger.new('/tmp/tf_app.log')
	task :ameblo, %w(ameblo_id months) do |_task, args|
		m = (args.months || '30').to_i
		today = Date.today
		(0..m - 1).each do |i|
			yyyymm = (today << i).strftime('%Y%m')
			url = "http://ameblo.jp/#{args.ameblo_id}/imagelist-#{yyyymm}.html"
			logger.info(url)
			doc = Nokogiri::HTML(open(url, options))
			doc.css('#imgList .imgLink').each do |li|
				img_url = li[:href]
				logger.info(img_url)
				targets = Nokogiri::HTML(open(img_url, options)).css('script').select do |script|
					script.text.match(/imgData/)
				end
				data = JSON.parse(targets.first.text.scan(/{.*}/m)[0])
				images = data['imgData']['next']['imgList'].concat(data['imgData']['current']['imgList'])
				images.each do |image|
					uid = ['ameblo', args.ameblo_id, image['imgUrl'].split('/').last.split('.').first].join(':')
					Photo.find_or_create_by(uid: uid) do |p|
						p.source_url = URI(data['pageDomain'] + image['pageUrl']).to_s
						p.photo_url = URI(data['imgDetailDomain'] + image['imgUrl']).to_s
						p.caption = image['title']
						p.posted_at = image['date']
						print p.source_url
						print "\n"
						print p.photo_url
						print "\n"
						print p.caption
						print "\n"
						print p.posted_at
						print "\n---\n"
					end
				end
				sleep 1
			end
		end

	end
end
