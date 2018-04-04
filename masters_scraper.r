source('C:/Users/cheiser/code/github/codyr/utilityfunctions.r',chdir = T)

# initialize final data frame
CompleteData <- data.frame(rndNum = numeric(0),
                           courseNum = numeric(0),
                           rndPos = character(0),
                           rndScr = numeric(0),
                           relParScr= character(0),
                           cumParScr = character(0),
                           playerName = numeric(0),
                           year = numeric(0),
                           name = character(0))

years <- c(1997:2017) # years to query

for(j in 1:length(years)){
  # get link to JSON version of data pages on PGA website
  JSONLink <- paste0("http://www.pgatour.com/data/R/014/",years[j],"/tournsum.json")
  # initialize frame for dumping data into
  temp <- data.frame(rndNum = numeric(0),
                     courseNum = numeric(0),
                     rndPos = character(0),
                     rndScr = numeric(0),
                     relParScr= character(0),
                     cumParScr = character(0),
                     playerName = numeric(0),
                     year = numeric(0),
                     name = character(0))
  
  JSONData <- fromJSON(txt=paste0("http://www.pgatour.com/data/R/014/",years[j],"/tournsum.json"), flatten= F)
  plrNums <- JSONData$years$tours[[1]]$trns[[1]]$plrs[[1]]$plrNum
  plrScores <- JSONData$years$tours[[1]]$trns[[1]]$plrs[[1]]$rnds
  print(paste(as.numeric(JSONData$years$year), years[j]))
  
  for(i in 1:length(plrScores)){
    if(length(plrScores[[i]]$rndNum) > 0){
      plrScores[[i]]$playerName <- rep(plrNums[i], times = length(plrScores[[i]]$rndNum))
      plrScores[[i]]$year <- rep(as.numeric(JSONData$years$year), 
                                 times = length(plrScores[[i]]$rndNum))
      plrScores[[i]]$name <- paste(JSONData$years$tours[[1]]$trns[[1]]$plrs[[1]]$name$first[i], 
                                   JSONData$years$tours[[1]]$trns[[1]]$plrs[[1]]$name$last[i])
    }
  }  
  
  for(i in 1:length(plrScores)){
    temp <- rbind(temp, plrScores[[i]])
  }
  
  CompleteData <- rbind(CompleteData, temp)
  temp <- NULL
}

# now some downstream manipulation of the frame before saving
CompleteData$First <- vectorsplit(CompleteData$name,'\\ ',keep = 1)
CompleteData$Last <- vectorsplit(CompleteData$name,'\\ ',keep = 2)

# CompleteData %>%
#   select(rndNum, rndScr, playerName, year, name) %>% 
#   tidyr::spread(rndNum, rndScr) %>% 
#   rename('Round1.Score' = 'Round 1', 'Round2.Score' = 'Round 2', 'Round3.Score' = 'Round 3', 'Round4.Score' = 'Round 4') -> scores
# 
# CompleteData %>%
#   select(rndNum, rndPos, playerName, year, name) %>%
#   tidyr::spread(rndNum, rndPos) %>% 
#   rename('Round1.Pos' = 'Round 1', 'Round2.Pos' = 'Round 2', 'Round3.Pos' = 'Round 3', 'Round4.Pos' = 'Round 4') -> positions
# 
# master <- dplyr::full_join(scores, positions, by = c('playerName','year','name'))

# import 2018 field
field.2018 <- read.csv('mastersfield2018.csv')
field.2018$First <- vectorsplit(field.2018$name,'\\ ',keep = 1)
field.2018$Last <- vectorsplit(field.2018$name,'\\ ',keep = 2)

left_join(field.2018,CompleteData,by = c('First','Last')) %>%
  select(-name.x) %>%
  rename('Player.ID'='playerName','Full.Name'='name.y') ->
  conglomerate

# data to work with
conglomerate %>% 
  filter(!is.na(year)) -> master

# list of players I don't have data on
conglomerate %>% 
  filter(is.na(year)) %>% 
  select(First,Last,group) -> no.info
write.csv(no.info,'no-info-players.csv',row.names = F)

################################################################################################################################
master$rndScr <- as.numeric(master$rndScr)

master %>%
  ggplot(aes(x = rndNum, y = rndScr, color = Full.Name)) + 
  geom_hline(yintercept = 72) +
  geom_jitter(width = 0.2, size = 2.5, alpha = 0.5, aes(label = year)) + 
  labs(x = NULL, y = 'Score', color = 'Golfer') + 
  plot.opts -> scores
scores
ggplotly(scores)

count(master, Full.Name, rndNum) %>% 
  filter(rndNum != 'Round 1') %>% 
  filter(rndNum != 'Round 2') %>% 
  group_by(Full.Name) %>% 
  summarise(n_weekends = mean(n)) -> weekends

count(master, Full.Name, rndNum) %>% 
  filter(rndNum != 'Round 3') %>% 
  filter(rndNum != 'Round 4') %>% 
  group_by(Full.Name) %>% 
  summarise(n_tries = mean(n)) -> visits

merge(weekends, visits, by='Full.Name') -> ratio
ratio$percent <- round(ratio$n_weekends/ratio$n_tries,3)*100
ratio$First <- vectorsplit(ratio$Full.Name,'\\ ',keep = 1)
ratio$Last <- vectorsplit(ratio$Full.Name,'\\ ',keep = 2)

ratio <- merge(ratio,field.2018[c('First','Last','group')],by = c('First','Last'),all.x = T, all.y = F)
write.csv(ratio, 'weekend-percent.csv',row.names = F)
