# Language-Tutor-French

Language-Tutor-French is a working solution of a personal language tutoring project that uses AWS Amazon Polly's neural voices to generate (close to) natural sounding native voice recording in English and French.

### How does it help language learning?
When learning words in a foreign language, having it saved in our long-term memory requires that we encounter it on average seven times (sufficiently spread out in time). Therefore, a huge and often neglected element of language learning is regular revision. This was my rationale when I decided to work on this project, since my goal in the spring of 2021 was to rebuild my French and achieve fluency again. The script randomly samples words and corresponding sentences and reads them aloud in a specific order (word in English, word in French, sentence in French, sentence in English, sentence again in French) to optimize word retention. Random sampling is performed using a trinagular distribution to ensure that newly learned words (i.e. words entered into the spreadsheet at a later stage) will have a higher probability to be read out by the script in an early stage. 

### How do I use it in my language learning?
I learn new words and update the spreadsheet on a regular basis. I created a .bat file and a Windows scheduled task based on it which launches the script every morning around my morning wake up. This way I ensure that words I encountered once and added in the spreadsheet will be regularly encountered in the future until they stick in my memory. I found that this strategy is a highly efficient and relatively passive method of developing one's languag eskills.

### Further steps
The script can easily be customizable to any of the languages currently supported by Amazon Polly. As a future improvement step, I am also considering adding a score to each word to signify the total number they were read out aloud. Those with a higher score will gradually be presented less and less frequently. Additionally, adding an upper limit of words to revise each day (e.g. 50 or 100, as an input parameter) would also be a useful additional feature.  