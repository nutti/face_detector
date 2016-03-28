require 'open-uri'
require 'date'
require 'logger'
require 'nokogiri'
require 'json'

require 'net/http'
require 'uri'
require 'rmagick'

require 'twitter'


namespace :tf_app do
    PROXY_FILE = 'proxy.json'
    PROXY_FILE.freeze
    TWITTER_FILE = 'twitter.json'
    TWITTER_FILE.freeze

	data = open(PROXY_FILE) do |io|
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

	task :twitter, %w(search_word num_tweets) do |_task, args|
        tw_data = open(TWITTER_FILE) do |io|
            JSON.load(io)
        end
        client = Twitter::REST::Client.new do |config|
            config.consumer_key = tw_data['consumer_key']
            config.consumer_secret = tw_data['consumer_secret']
            config.access_token = tw_data['access_token']
            config.access_token_secret = tw_data['access_token_secret']
            config.proxy = data['proxy_ipuri']
        end
        print("searching images...\n")
        tweets = client.search("#{args.search_word} filter:images -filter:retweets", lang: 'ja', locale: 'ja').take(args.num_tweets.to_i)
        print("downloading images...\n")
        img_count = 0
        client.statuses(tweets, include_entities: true).each do |tweet|
            tweet.media.each do |media|
                uid = ['twitter', media.id].join(':')
                open(media.media_url_https, options) {|f|
                    outdir = "images/"
                    ext = File.extname(media.media_url_https)
                    filename = outdir + img_count.to_s + ext
                    File.open(filename, "wb") do |file|
                        file.puts f.read
                    end
                    print("downloaded: " + media.media_url_https + " (saved as " + filename + ")\n")
                }
                img_count += 1
            end
        end
        print(img_count.to_s + " images are downloaded.\n")
    end

end
