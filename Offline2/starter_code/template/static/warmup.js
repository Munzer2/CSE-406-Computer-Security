/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;

function readNlines(n) {
  /*
   * Implement this function to read n cache lines.
   * 1. Allocate a buffer of size n * LINESIZE.
   * 2. Read each cache line (read the buffer in steps of LINESIZE) 10 times.
   * 3. Collect total time taken in an array using `performance.now()`.
   * 4. Return the median of the time taken in milliseconds.
   */
  const buffer = new Uint8Array(n * LINESIZE);
  const times = [];
  let rand = 0; 
  for(let i = 0 ; i < 10; ++i) {
    const strt = performance.now();
    for(let j = 0 ; j < n * LINESIZE; j+= LINESIZE) {
      rand ^= buffer[j]; 
    }
    const end = performance.now();
    times.push(end - strt);
  }
  if(rand == 0xfaafaafa) { console.log(rand);}
  times.sort((a , b) => a - b);
  const median = times[Math.floor(times.length / 2)];
  return median;
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = [];

    /* Call the readNlines function for n = 1, 10, ... 10,000,000 and store the result */
    for(let n = 1; n <= 10000000; n *= 10) {
      try {
        const med = readNlines(n);
        results.push({
          time: med,
          n: n
        });
      }
      catch (err) {
        break;
      }
    }

    self.postMessage(results);
  }
});
