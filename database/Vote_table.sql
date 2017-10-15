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


