export interface UserCreate {
    email: string,
    full_name: string,
    password: string
}

export interface UserLogin {
    email: string,
    password: string
}