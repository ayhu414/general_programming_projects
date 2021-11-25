/*
 * CMSC 12300 - Computer Science with Applications 3
 * Borja Sotomayor, 2013 (original code)
 * Matthew Wachs, 2016 (port to C)
 *
 * An implementation of the thread pool pattern.
 * This file contains the implementation of the worker threads
 *
 * See WorkerThread.h for details.
 */

#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include "ThreadPool.h"
#include "WorkerThread.h"

WorkerThread* worker_init(ThreadPool* pool) {
    WorkerThread* t = (WorkerThread*)malloc(sizeof(WorkerThread));
    
    t->pool = pool;

    return t;
}

void worker_free(WorkerThread* t) {
    free(t);
}

void worker_start(WorkerThread* t) {
	// Create the thread and make it run the run() function
    pthread_create(&t->thd, NULL, worker_run, (void*)t);
}

void* worker_run(void* tv) {
    WorkerThread* t = (WorkerThread*)tv;
    while(!(t->pool->stop)){
        //Runs iff there are no stop calls
        pthread_mutex_lock(&t->pool->m);
        while(queue_length(t->pool->q) == 0){
            if(t->pool->stop){
                //if there is a stop call, unlock mutex
                pthread_mutex_unlock(&t->pool->m);
                return NULL;
            }
            pthread_cond_wait(&t->pool->cvQueueNonEmpty, &t->pool->m);
        }
        if(!(t->pool->stop) && (queue_length(t->pool->q) > 0)){
            USAGovClickTask* task = queue_dequeue(t->pool->q);
            pthread_mutex_unlock(&t->pool->m);
            task_run(task);
        }
    }
    pthread_mutex_unlock(&t->pool->m);
    return NULL;
}
