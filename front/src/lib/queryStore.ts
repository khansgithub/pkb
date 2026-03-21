import { writable } from "svelte/store";
import type { Snippet } from "./types";

export const queryStore = writable<Snippet[] | null>(null);