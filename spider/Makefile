
NAME = spider

SRCS = 	spider.py
PYTHON = python3

all: $(NAME)

$(NAME): $(NAME).py
	@chmod +x $<
	@ln -sf $< $@

clean:
	rm -rf *.pyc __pycache__

fclean: clean
		rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re