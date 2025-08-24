var noise_freq = $state(0.2);

export function updateNoiseInternal(): number {
    let t = setInterval(() => {
        let n = Math.random() * (1 - -0.5) + -0.5;
        noise_freq += n;
        // noise_freq = jitterInRange(noise_freq);
        // console.log(noise_freq)
    }, 1000 / 12);
    return t;
}

export function get_noise(freq: number | null) {
    return noise(freq);
}


export function noise1(f: number | null) {
    // black background
    return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><filter id='noiseFilter'><feTurbulence type='fractalNoise' baseFrequency='${f}' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23noiseFilter)'/></svg>`;
};

export function noise(f: number | null) {
    // transparent background
    return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' version='1.1' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:svgjs='http://svgjs.dev/svgjs' viewBox='0 0 700 700' width='700' height='700' opacity='1'%3E%3Cdefs%3E%3Cfilter id='nnnoise-filter' x='-20%25' y='-20%25' width='140%25' height='140%25' filterUnits='objectBoundingBox' primitiveUnits='userSpaceOnUse' color-interpolation-filters='linearRGB'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='${f || noise_freq}' numOctaves='4' seed='15' stitchTiles='stitch' x='0%25' y='0%25' width='100%25' height='100%25' result='turbulence'%3E%3C/feTurbulence%3E%3CfeSpecularLighting surfaceScale='11' specularConstant='3' specularExponent='20' lighting-color='%23ffffff' x='0%25' y='0%25' width='100%25' height='100%25' in='turbulence' result='specularLighting'%3E%3CfeDistantLight azimuth='3' elevation='98'%3E%3C/feDistantLight%3E%3C/feSpecularLighting%3E%3CfeColorMatrix type='saturate' values='0' x='0%25' y='0%25' width='100%25' height='100%25' in='specularLighting' result='colormatrix'%3E%3C/feColorMatrix%3E%3C/filter%3E%3C/defs%3E%3Crect width='700' height='700' fill='transparent'%3E%3C/rect%3E%3Crect width='700' height='700' fill='%23ffffff' filter='url(%23nnnoise-filter)'%3E%3C/rect%3E%3C/svg%3E`;
};

export function cn(class_array: string[], class_names?: string): string;
export function cn(class_array: string[][], class_names?: string): string;
export function cn(
    class_array: string[][] | string[],
    class_names?: string,
): string {
    return `${class_array.flat().join(" ")} ${class_names || ""}`;
}

export var c = {
    noise: {
        css: [
            "fixed",
            "h-screen",
            // "invert-100",
            "left-0",
            "m-0",
            // "mix-blend-luminosity",
            "mix-blend-overlay",
            "opacity-20",
            "p-0",
            "point-none",
            "top-0",
            "w-screen",
        ],
    },
    id_middle: {
        clipper: {
            css: [
                "!bg-none/0",
                // "!blur-sm",
                // "!blur-[6px]",
                "!overflow-hidden",
                "!p-0",
                "!pointer-events-none",
                "!shadow-none",
                "!top-2",
                // "!bg-opacity-0",
                // "!p-2",
            ],
            hover: {
                css: [
                    "-mt-[250px]",
                    "absolute",
                    "bg-white",
                    "blur-xl",
                    "h-[500px]",
                    "mix-blend-overlay",
                    "rounded-full",
                    "w-[100px]",
                    // "aspect-square",
                    // "h-screen",
                    // "opacity-0"
                    // "w-40",
                ],
            },
        },
        back_glow: {
            css: [
                "!shadow-emerald-400",
                "!shadow-lg",
                "opacity-50",
                "pointer-events-none",
            ],
        },
        input: {
            css: [
                "absolute",
                "bg-black/0",
                "h-[5vw]",
                "-mt-[2.5vw]",
                "px-5",
                "rounded-full",
                // "text-4xl",
                "text-center",
                "text-gray-100",
                "w-full",
            ],
        },
    },
};