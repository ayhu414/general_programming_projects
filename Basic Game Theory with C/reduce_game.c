/* CS 123, Spring 2020
 * Basic game theory: Reducing Games
 *
 * Reduce games using iterative elimination.
 *
 * Allen (Yixin) Hu
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <assert.h>
#include "reduce_game.h"

int comp_array(double* x1, double* x2, int *n){
  /*
  * compares two arrays, and reports the
  * comparison score in agg; for every element
  * of array x1 that is greater than x2, agg++,
  * and vice versa
  */
    int agg = 0;
    for(int i = 0; i < *n; i++){
        if(*(x1 + i) < *(x2 + i)){
            agg++;
        }
        else if(*(x1 + i) > *(x2 + i)){
            agg--;
        }
    }
    return agg;
}

int p2_turn(game_t *g){
/*
*  modifies the game table by reducing rows
*  returns 1 if removed, returns 0 if no removals
*/
  double **p2 = (*g)->player2;
  int n = (*g)->n;
  int m = (*g)->m;
  double T_p2[m][n];

  /*
  * transposes the p2 matrix to use the
  * general array comparison function.
  * uses results from transpose to remove
  * columns from original p2 matrix
  * */
  for(int i = 0; i < m; i++){
    for(int j = 0; j < n; j++){
      T_p2[i][j] = p2[j][i];
    }
  }

  for(int i = 0; i < m; i++){
      for(int j = i+1; j < m; j++){
          int res = comp_array(*(T_p2+i),*(T_p2+j),&n);
          if(res == n){
              remove_col_game(*g,i);
              return 1;
          }
          if(res == n*(-1)){
              remove_col_game(*g,j);
              return 1;
          }
      }
  }
  return 0;
}

int p1_turn(game_t *g){
/*
*  modifies the game table by reducing rows
*  returns 1 if removed, returns 0 if no removals
*/
  double **p1 = (*g)->player1;
  int n = (*g)->n;
  int m = (*g)->m;
  
  for(int i = 0; i < n; i++){
      for(int j = i+1; j < n; j++){
          int res = comp_array(*(p1+i),*(p1+j),&m);
          if(res == m){
              remove_row_game(*g,i);
              return 1;
          }
          if(res == m*(-1)){
              remove_row_game(*g,j);
              return 1;
          }
      }
  }
  return 0;
}

void reduce(game_t g) {
/* reduce: iteratively reduce rows and columns until no changes occur.
 *  game_t g: the game
 *
 *  Modifies the game, if there are rows or columns that can be reduced.
 */
  int reduce_col = 1;
  int reduce_row = 1;
  
  while(reduce_row == 1 || reduce_col == 1){
    /*if statements so that row/col
    does not reduce unnecessarily*/
    if(reduce_row == 1){
      reduce_row = p1_turn(&g);
    }
    if(reduce_col == 1){
      reduce_col = p2_turn(&g);
    }
    } 
}