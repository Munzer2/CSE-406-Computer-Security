/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;
/* Find the L3 size by running `getconf -a | grep CACHE` */
const LLCSIZE =25165824; 
/* Collect traces for 10 seconds; you can vary this */
const TIME = 10000;
/* Collect traces every 10ms; you can vary this */
const P = 10; 
const buf = new Uint8Array(LLCSIZE);

function sweep(P) {
    /*
     * Implement this function to run a sweep of the cache.
     * 1. Allocate a buffer of size LLCSIZE.
     * 2. Read each cache line (read the buffer in steps of LINESIZE).
     * 3. Count the number of times each cache line is read in a time period of P milliseconds.
     * 4. Store the count in an array of size K, where K = TIME / P.
     * 5. Return the array of counts.
     */
    const counts = []; 
    const K = Math.floor(TIME / P); 

    for(let i = 0; i < K; ++i) {
        const strt = performance.now();
        let c = 0 ;
        while(performance.now() - strt < P) {
            for(let j = 0; j < LLCSIZE; j += LINESIZE) {
                buf[j]; // Access each cache line
            }
            c++;  
        }
        counts.push(c);
    }
    return counts; 
}   

self.addEventListener('message', function(e) {
    /* Call the sweep function and return the result */
});