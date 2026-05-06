import java.io.*;
import java.util.*;

public class Sol1 {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        long[] w = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++)
            w[i] = Long.parseLong(st.nextToken());
        Arrays.sort(w);  // ascending, will read from end

        long[] diff = new long[n + 2];
        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int l = Integer.parseInt(st.nextToken());
            int r = Integer.parseInt(st.nextToken());
            diff[l]++;
            diff[r + 1]--;
        }

        long[] popcount = new long[n];
        long running = 0;
        for (int i = 1; i <= n; i++) {
            running += diff[i];
            popcount[i - 1] = running;
        }
        Arrays.sort(popcount);  // ascending, will read from end

        long result = 0;
        for (int i = 0; i < n; i++) {
            result += w[i] * popcount[i];  // both ascending: largest * largest
        }
        System.out.println(result);
    }
}
