create extension if not exists "citext";


CREATE TABLE "User"
(
  id SERIAL PRIMARY KEY NOT NULL,
  about TEXT,
  email CITEXT COLLATE pg_catalog.ucs_basic NOT NULL CONSTRAINT User_email_unique UNIQUE,
  fullname VARCHAR(100) NOT NULL,
  nickname CITEXT COLLATE pg_catalog.ucs_basic NOT NULL CONSTRAINT User_nickname_unique UNIQUE
);



CREATE TABLE "Forum"
(
    id SERIAL PRIMARY KEY NOT NULL,
    posts INT NOT NULL DEFAULT 0,
    slug CITEXT COLLATE pg_catalog.ucs_basic NOT NULL CONSTRAINT Forum_slug_unique UNIQUE,
    threads INT NOT NULL DEFAULT 0,
    title VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,

  CONSTRAINT Forum_user_id_fk FOREIGN KEY (user_id)
   REFERENCES public."User" (id) MATCH SIMPLE
   ON UPDATE NO ACTION ON DELETE NO ACTION

);



CREATE TABLE Thread
(
    id SERIAL PRIMARY KEY NOT NULL,
	author_id INT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT now(),
    forum_id INT NOT NULL,
	message TEXT NOT NULL,
	slug CITEXT COLLATE pg_catalog.ucs_basic ,
    title VARCHAR(200) NOT NULL,
   votes INT DEFAULT 0,

      CONSTRAINT Thread_Forum_id_fk FOREIGN KEY (forum_id)
      REFERENCES public."Forum" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT Thread_User_id_fk FOREIGN KEY (author_id)
      REFERENCES public."User" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
      CONSTRAINT thread_slug_unique UNIQUE (slug)
);


CREATE TABLE Post
(
    id SERIAL PRIMARY KEY NOT NULL,
    author_id INT NOT NULL,
    created TIMESTAMP with time zone DEFAULT now() NOT NULL,
    forum_id INT NOT NULL,
    isEdited BOOLEAN DEFAULT FALSE NOT NULL,
    message TEXT NOT NULL,
    parent INT NOT NULL DEFAULT 0,
    thread_id INT NOT NULL,


 CONSTRAINT Post_forum_id_fk FOREIGN KEY (forum_id)
      REFERENCES public."Forum" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT Post_thread_id_fk FOREIGN KEY (thread_id)
      REFERENCES public.thread (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT Post_user_id_fk FOREIGN KEY (author_id)
      REFERENCES public."User" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE Vote
(
    id SERIAL PRIMARY KEY NOT NULL,
    thread_id INT NOT NULL,
    user_id INT NOT NULL,
    vote INT NOT NULL,


      CONSTRAINT Vote_thread_id_fk FOREIGN KEY (thread_id)
      REFERENCES public.thread (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT Vote_user_id_fk FOREIGN KEY (user_id)
      REFERENCES public."User" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,

      CONSTRAINT  Vote_thread_id_user_id_unique UNIQUE (thread_id,user_id)


);