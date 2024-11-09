build: 
	docker build . -t abcd

run:
	docker run -it --rm -p 8000:8000 abcd
	