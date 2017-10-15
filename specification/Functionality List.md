# Functionality List

## Basic Functions

### Game (Yupeng)

#### StartGame

##### Initialize

This function initialize the status of a new table.

##### Shuffle

This function shuffle the cards, generate a random sequence of cards.

##### AllocateCounter

This function decide the player who will pay blind counter on the table, deduct the money from the player's account and put it into the pool.

#### Player

##### Hold

This function deals with the event that the player choose to hold this turn, it record the status and let the next player decide.

##### Fold

This function deals with the event that the player choose to fold this game, it let the player choose to show/not show his/her cards and change the player's status from playing to watching.

##### Raise

This function deals with the event that the player choose to raise counter, it let the player choose how much he/she want to raise, record this information and let the next player to decide.

#### Dealer

##### AllocateInitialCard

This function allocate each player two new cards after they decide whether they are in/out the game.

##### AllocateCard

This function allocate one new card to the table.

##### Judge

When players play to the end of the last round, dealer will let all player show their cards and compare their card combination to decide who will win the game. When all other player give up except one, dealer will give all the counter in the pool to this player.

### Social (Du, Shuangning)

#### Account

##### Register/Login/Logout

These functions let the player have his/her own account just like grumblr, and each account will record their money, bio and other game information.

##### JoinTable

This function let the player choose a table to watch/play the game. The first one in this table will be the owner of the table.

##### StartTable

The owner of the table will has the right to start the game when the number of players in this table is greater than 2.

##### QuitTable

The player can exit the table, the function will update the information of the table and the game and change the ownership of the table.

##### MakeFriend

This function let the player send a request to another player and the other one can accept/reject. Once accept, the two player can be friend and be shown in each other's friend list.

## Optional Functions (Du, Shuangning, Yupeng)

### StatisticVisualization

These functions will statistic and analyse the player's playing history and draw a picture for them to let them know their playing pattern directly in a webpage.

### AI

Player can exercise with AI of different difficulty.

### Matching

Player can be recommend and match to player who has samiliar level.

### Other Idea

To be Done.

